import requests

from app.services import senado_client


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_get_returns_json_with_accept_header(mocker):
    get = mocker.patch(
        "app.services.senado_client.requests.get",
        return_value=DummyResponse([{"id": 1}]),
    )

    result = senado_client._get("/processo", {"sigla": "PL"})

    assert result == [{"id": 1}]
    get.assert_called_once_with(
        f"{senado_client.BASE_URL}/processo",
        params={"sigla": "PL"},
        headers={"Accept": "application/json"},
        timeout=senado_client.TIMEOUT,
    )


def test_get_returns_none_when_request_fails(mocker):
    mocker.patch(
        "app.services.senado_client.requests.get",
        side_effect=requests.exceptions.ConnectionError("offline"),
    )

    assert senado_client._get("/processo") is None


def test_pesquisar_materias_handles_list_response_and_params(mocker):
    get = mocker.patch(
        "app.services.senado_client._get",
        return_value=[{"id": 10, "identificacao": "PL 10/2026"}],
    )

    result = senado_client.pesquisar_materias(
        keyword="feminicidio",
        sigla_tipo="PL",
        ano_inicial=2020,
        numdias=2,
    )

    assert result == [{"id": 10, "identificacao": "PL 10/2026"}]
    get.assert_called_once_with(
        "/processo",
        {
            "sigla": "PL",
            "termo": "feminicidio",
            "v": 1,
            "dataInicioApresentacao": "2020-01-01",
            "numdias": 2,
        },
    )


def test_pesquisar_materias_normalizes_dict_payloads(mocker):
    mocker.patch(
        "app.services.senado_client._get",
        return_value={"Processos": {"id": 42}},
    )

    assert senado_client.pesquisar_materias("mulher", "PL") == [{"id": 42}]


def test_pesquisar_materias_returns_empty_list_for_unexpected_payload(mocker):
    mocker.patch("app.services.senado_client._get", return_value="invalid")

    assert senado_client.pesquisar_materias("mulher", "PL") == []


def test_buscar_senador_uses_cache(mocker):
    senado_client._cache_senadores.clear()
    get = mocker.patch(
        "app.services.senado_client._get",
        return_value={"DetalheParlamentar": {"Parlamentar": {"id": 9}}},
    )

    first = senado_client.buscar_senador(9)
    second = senado_client.buscar_senador(9)

    assert first == second
    get.assert_called_once_with("/senador/9")
