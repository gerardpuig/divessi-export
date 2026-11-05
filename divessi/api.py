import requests

from .constants import BASE_URL, SSI_APP_PARAMS, SSI_HEADERS, TANK_TYPES
from .exceptions import AuthenticationException


class SSIApi:
    token = None

    def __init__(self, username: str, password: str) -> None:
        if not self.token:
            self.token = self._authenticate(username, password)

    def _get_json(self, what: str, **params) -> dict:
        response = requests.get(
            BASE_URL,
            params={
                **SSI_APP_PARAMS,
                "what": what,
                **params,
            },
            headers=SSI_HEADERS,
        )

        if response.status_code != 200:
            response.raise_for_status()

        response_data = response.json()
        if response_data.get("status") in (401, "401"):
            raise AuthenticationException(
                "SSI rejected the token. Sign in again and retry the export."
            )
        if response_data.get("authenticated") is False:
            message = (
                "SSI rejected the credentials."
                if what == "authenticate"
                else "SSI rejected the token. Sign in again and retry the export."
            )
            raise AuthenticationException(message)

        return response_data

    def _authenticate(self, username: str, password: str) -> str:
        response_data = self._get_json("authenticate", l=username, p=password)
        if "token" not in response_data:
            raise AuthenticationException

        return response_data["token"]

    def get_wildlife(self) -> list:
        response_data = self._get_json("get_wildlife_vars", token=self.token)
        wildlife = {}
        for animal in response_data["wildlife"]["animal"]:
            wildlife[animal["id"]] = animal["title_key"]

        return wildlife

    def get_divelog(self) -> list:
        wildlife = self.get_wildlife()
        response_data = self._get_json("get_divelog", token=self.token)

        sites_map = {}
        for site in response_data["logbook_sites"]:
            sites_map[site["odin_dive_sites_id"]] = site["odin_dive_sites_name"]

        logbook = []
        for divelog in response_data["logbook_details"]:
            nitrox_percent = divelog["odin_user_log_ean_percent"]

            animals = [
                wildlife[animal_id] for animal_id in divelog["odin_user_log_animal_ids"]
            ]

            logbook.append(
                dict(
                    number=divelog["odin_user_log_nr"],
                    site=sites_map[divelog["odin_user_log_dive_sites_id"]],
                    date=divelog["odin_user_log_date"],
                    time=divelog["odin_user_log_entry_time"],
                    divetime=divelog["odin_user_log_divetime"],
                    comments=divelog["odin_user_log_comment"],
                    depth=divelog["odin_user_log_depth_m"],
                    water_temp=divelog["odin_user_log_watertemp_c"],
                    water_temp_max=divelog["odin_user_log_watertemp_max_c"],
                    weight=divelog["odin_user_log_weight_kg"],
                    tank_type=TANK_TYPES[divelog["odin_user_log_var_tanktype_id"]]
                    if divelog["odin_user_log_var_tanktype_id"]
                    else "",
                    tank_size=divelog["odin_user_log_tank_vol_l"],
                    gas=f"Nitrox {nitrox_percent}%"
                    if divelog["odin_user_log_ean"]
                    else "Air",
                    start_bar=divelog["odin_user_log_pressure_start_bar"],
                    end_bar=divelog["odin_user_log_pressure_end_bar"],
                    avg_depth=divelog["odin_user_log_avg_depth_m"],
                    consumption_l=divelog["odin_user_log_amv_l"],
                    gear_details=divelog["odin_user_log_gear_details"],
                    animals=", ".join(animals),
                    divecenter=divelog["odin_user_log_divecenter_confirmed_name"],
                    depth_dataset=divelog["odin_user_log_depthDataset"],
                    temp_dataset=divelog["odin_user_log_tempDataset"],
                )
            )

        return logbook
