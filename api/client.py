import requests

BASE_URL = "https://api.pahrul.my.id/api/posts"

class PostAPI:
    @staticmethod
    def get_all():
        try:
            r = requests.get(BASE_URL, timeout=10)
            if r.status_code == 200:
                return r.json(), r.status_code
            return {"data": []}, r.status_code
        except Exception:
            return {"data": []}, 500

    @staticmethod
    def create(data):
        try:
            r = requests.post(BASE_URL, json=data, timeout=10)
            if r.status_code in [200, 201, 422]:
                return r.json(), r.status_code
            return {"message": "Gagal"}, r.status_code
        except Exception:
            return {"message": "Error"}, 500

    @staticmethod
    def update(id, data):
        try:
            r = requests.put(f"{BASE_URL}/{id}", json=data, timeout=10)
            if r.status_code in [200, 204, 422]:
                try:
                    return r.json(), r.status_code
                except:
                    return {}, r.status_code
            return {"message": "Gagal"}, r.status_code
        except Exception:
            return {"message": "Error"}, 500

    @staticmethod
    def delete(id):
        try:
            r = requests.delete(f"{BASE_URL}/{id}", timeout=10)
            return r.status_code
        except Exception:
            return 500