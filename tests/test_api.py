from unittest import mock

import pytest
import requests_mock

from divessi.api import SSIApi
from divessi.constants import BASE_URL, SSI_APP_PARAMS, SSI_HEADERS
from divessi.exceptions import AuthenticationException


def test_authenticate():
    username = "email"
    password = "password"

    with requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?what=authenticate",
            json={"authenticated": True, "token": "success"},
        )
        api = SSIApi(username, password)

    assert api.token == "success"
    assert m.last_request.headers["User-Agent"] == SSI_HEADERS["User-Agent"]
    assert m.last_request.headers["Accept"] == "application/json"
    assert all(
        m.last_request.qs[key.lower()] == [value.lower()]
        for key, value in SSI_APP_PARAMS.items()
    )


def test_authenticate_error():
    username = "email"
    password = "password"

    with requests_mock.Mocker() as m, pytest.raises(AuthenticationException):
        m.get(
            f"{BASE_URL}?what=authenticate",
            json={},
        )
        api = SSIApi(username, password)

        assert api.token is None


def test_get_divelog():
    username = "email"
    password = "password"
    token = "token"

    with mock.patch(
        "divessi.api.SSIApi._authenticate", return_value=token
    ), requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?what=get_wildlife_vars",
            json={"wildlife": {"animal": []}},
        )
        m.get(
            f"{BASE_URL}?what=get_divelog",
            json={
                "logbook_sites": [
                    {"odin_dive_sites_id": 1, "odin_dive_sites_name": "Thistlegorm"}
                ],
                "logbook_details": [
                    {
                        "odin_user_log_nr": 1,
                        "odin_user_log_dive_sites_id": 1,
                        "odin_user_log_date": "2023-09-06",
                        "odin_user_log_entry_time": "10:00",
                        "odin_user_log_divetime": 43,
                        "odin_user_log_comment": "amazing!",
                        "odin_user_log_depth_m": 33,
                        "odin_user_log_watertemp_c": 25,
                        "odin_user_log_watertemp_max_c": 27,
                        "odin_user_log_weight_kg": 8,
                        "odin_user_log_var_tanktype_id": 20,
                        "odin_user_log_tank_vol_l": 12,
                        "odin_user_log_ean": True,
                        "odin_user_log_ean_percent": 32,
                        "odin_user_log_pressure_start_bar": 200,
                        "odin_user_log_pressure_end_bar": 80,
                        "odin_user_log_avg_depth_m": 16.9,
                        "odin_user_log_amv_l": 13,
                        "odin_user_log_gear_details": "5mm",
                        "odin_user_log_divecenter_confirmed_name": "SSI Dive Center",
                        "odin_user_log_animal_ids": [],
                        "odin_user_log_depthDataset": [],
                        "odin_user_log_tempDataset": [],
                    }
                ],
            },
        )
        divelog = SSIApi(username, password).get_divelog()

    assert all(
        request.headers["User-Agent"] == SSI_HEADERS["User-Agent"]
        for request in m.request_history
    )
    assert all(
        request.qs[key.lower()] == [value.lower()]
        for request in m.request_history
        for key, value in SSI_APP_PARAMS.items()
    )
    assert len(divelog) == 1

    dive = divelog[0]

    assert dive["number"] == 1
    assert dive["site"] == "Thistlegorm"
    assert dive["date"] == "2023-09-06"
    assert dive["time"] == "10:00"
    assert dive["divetime"] == 43
    assert dive["comments"] == "amazing!"
    assert dive["depth"] == 33
    assert dive["water_temp"] == 25
    assert dive["water_temp_max"] == 27
    assert dive["weight"] == 8
    assert dive["tank_type"] == "Aluminium"
    assert dive["tank_size"] == 12
    assert dive["gas"] == "Nitrox 32%"
    assert dive["start_bar"] == 200
    assert dive["end_bar"] == 80
    assert dive["avg_depth"] == 16.9
    assert dive["consumption_l"] == 13
    assert dive["gear_details"] == "5mm"
    assert dive["divecenter"] == "SSI Dive Center"


def test_get_wildlife_encodes_token():
    username = "email"
    password = "password"
    token = "token+with&reserved=value"

    with mock.patch(
        "divessi.api.SSIApi._authenticate", return_value=token
    ), requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?what=get_wildlife_vars",
            json={"wildlife": {"animal": []}},
        )
        wildlife = SSIApi(username, password).get_wildlife()

    assert wildlife == {}
    assert m.last_request.qs["token"] == [token]
    assert m.last_request.headers["User-Agent"] == SSI_HEADERS["User-Agent"]


def test_get_wildlife_rejects_token_invalid_body():
    with mock.patch(
        "divessi.api.SSIApi._authenticate", return_value="token"
    ), requests_mock.Mocker() as m:
        m.get(
            f"{BASE_URL}?what=get_wildlife_vars",
            json={
                "status": 401,
                "result": "Token not valid (token_not_found)",
            },
        )

        with pytest.raises(AuthenticationException, match="Sign in again"):
            SSIApi("email", "password").get_wildlife()
