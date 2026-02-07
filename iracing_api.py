"""
iRacing API Client
Handles authentication and data retrieval from iRacing
"""

import aiohttp
import hashlib
import base64
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger('iRacingBot.API')

class iRacingAPI:
    BASE_URL = "https://members-ng.iracing.com"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.session = None
        self.authenticated = False
        self.auth_token = None
        self.auth_expires = None

    async def authenticate(self) -> bool:
        """Authenticate with iRacing"""
        # Check if we're already authenticated and token is still valid
        if self.authenticated and self.auth_expires and datetime.now() < self.auth_expires:
            return True

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Hash password as per iRacing requirements
            password_hash = hashlib.sha256((self.password + self.username.lower()).encode()).digest()
            encoded_password = base64.b64encode(password_hash).decode()

            # Authenticate
            async with self.session.post(
                f"{self.BASE_URL}/auth",
                json={
                    "email": self.username,
                    "password": encoded_password
                }
            ) as response:
                if response.status == 200:
                    self.authenticated = True
                    self.auth_expires = datetime.now() + timedelta(hours=1)
                    logger.info("Successfully authenticated with iRacing")
                    return True
                else:
                    logger.error(f"Authentication failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Error authenticating with iRacing: {e}")
            return False

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make an authenticated request to iRacing API"""
        if not await self.authenticate():
            return None

        try:
            url = f"{self.BASE_URL}{endpoint}"
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"API request failed: {response.status} - {endpoint}")
                    return None

        except Exception as e:
            logger.error(f"Error making API request to {endpoint}: {e}")
            return None

    async def get_member_info(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get information about an iRacing member"""
        data = await self._make_request(f"/data/member/get", params={"cust_ids": customer_id})

        if data and 'members' in data and len(data['members']) > 0:
            return data['members'][0]
        return None

    async def search_member(self, search_term: str) -> List[Dict[str, Any]]:
        """Search for iRacing members by name"""
        data = await self._make_request(
            f"/data/lookup/drivers",
            params={"search_term": search_term}
        )

        if data and 'results' in data:
            return data['results']
        return []

    async def get_league_info(self, league_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a league"""
        data = await self._make_request(f"/data/league/get", params={"league_id": league_id})
        return data

    async def get_league_roster(self, league_id: int) -> List[Dict[str, Any]]:
        """Get the roster for a league"""
        try:
            # Get league seasons
            seasons_data = await self._make_request(
                f"/data/league/seasons",
                params={"league_id": league_id}
            )

            if not seasons_data or 'seasons' not in seasons_data:
                logger.warning(f"No seasons found for league {league_id}")
                return []

            # Get the most recent season
            seasons = seasons_data['seasons']
            if not seasons:
                return []

            # Sort by season_id to get the latest
            latest_season = sorted(seasons, key=lambda x: x.get('season_id', 0), reverse=True)[0]
            season_id = latest_season['season_id']

            # Get roster for this season
            roster_data = await self._make_request(
                f"/data/league/season_standings",
                params={
                    "league_id": league_id,
                    "season_id": season_id
                }
            )

            if not roster_data or 'standings' not in roster_data:
                logger.warning(f"No roster found for league {league_id}, season {season_id}")
                return []

            # Extract member information
            roster = []
            for standing in roster_data['standings']:
                member_info = {
                    'cust_id': standing.get('cust_id'),
                    'display_name': standing.get('display_name'),
                    'car_number': standing.get('car_number', 0),
                    'helmet': standing.get('helmet', {}),
                }
                roster.append(member_info)

            logger.info(f"Retrieved {len(roster)} members from league {league_id}")
            return roster

        except Exception as e:
            logger.error(f"Error getting league roster: {e}")
            return []

    async def get_league_sessions(self, league_id: int, season_id: int = None) -> List[Dict[str, Any]]:
        """Get sessions for a league season"""
        params = {"league_id": league_id}
        if season_id:
            params["season_id"] = season_id

        data = await self._make_request(f"/data/league/season_sessions", params=params)

        if data and 'sessions' in data:
            return data['sessions']
        return []

    async def verify_member_exists(self, customer_id: int) -> bool:
        """Verify that an iRacing member exists"""
        member = await self.get_member_info(customer_id)
        return member is not None

    async def get_member_car_number(self, customer_id: int, league_id: int) -> Optional[int]:
        """Get the car number currently assigned to a member in a league"""
        roster = await self.get_league_roster(league_id)

        for member in roster:
            if member.get('cust_id') == customer_id:
                return member.get('car_number')

        return None

    async def close(self):
        """Close the API session"""
        if self.session:
            await self.session.close()
            self.session = None
            self.authenticated = False
