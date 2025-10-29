from fastapi import status

def test_create_customer(client):
    response = client.post(
        "/customers",
        json={
            "name": "Jhon Doe",
            "email": "jhondoe@test.com",
            "age": 40
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    # custoimer_id: int response.json()["id"]
    # response = client.get(
    #     f"/customers/{id}"
    # )