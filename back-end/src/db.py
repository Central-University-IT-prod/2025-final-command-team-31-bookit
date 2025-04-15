import hashlib
import json
import shutil
import uuid
import time
from logging import exception
from pathlib import Path
import psycopg2
import psycopg2.extras
import redis
import secrets
from cfg import *
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from models.users import UserPatch

ph = PasswordHasher()


def hashsha256(v:str):
    return hashlib.sha256(v.encode()).hexdigest()


def create_hash(password: str) -> str:
    return ph.hash(password)

def verify_password(hashed_password: str, password: str) -> bool:
    try:
        ph.verify(hashed_password, password)
        return True
    except VerifyMismatchError:
        return False

class DB:
    def __init__(self):
        self.postgre_con = psycopg2.connect(dbname=POSTGRES_DATABASE, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, port=POSTGRES_PORT)
        self.postgre_cur = self.postgre_con.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.redis_con = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

        self.role_to_price_field = {
            "GUEST": "price_g",
            "EMPLOYEE": "price_e",
            "ADMIN": "price_e",
            "SUPER_ADMIN": "price_e"
        }

    def end(self):
        self.postgre_cur.close()
        self.postgre_con.close()
        self.redis_con.close()

    def create_token(self, user_id, ex):
        idhash = hashsha256(user_id)
        for i in self.redis_con.scan_iter(match=f"B.{idhash}.*"):
            self.redis_con.delete(i)

        # create new session
        session_key = f"B.{idhash}.{secrets.token_hex(32)}"
        self.redis_con.set(session_key, user_id, ex=ex)
        return session_key

    def add_user(self, user):
        role = user.role
        password_hash = create_hash(user.password)

        qr_code = secrets.token_hex(32)

        self.postgre_cur.execute(
            "INSERT INTO users (role, login, name, surname, secondname, password_hash, email, contacts, qr_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (role, user.login, user.name, user.surname, user.second_name, password_hash, user.email, user.contacts, qr_code))
        user_id = self.postgre_cur.fetchone()[0]
        ex = 24 * 60 * 60
        token = self.create_token(user_id, ex)

        self.postgre_con.commit()

        return token

    def get_user_by_logpass(self, login, password, remember_me=False):
        # password_hash = create_hash(password)
        self.postgre_cur.execute(
            "SELECT * FROM users WHERE login=%s",
            (login,))
        user = self.postgre_cur.fetchone()

        if user:
            if not verify_password(user["password_hash"], password):
                return None
            user_id = user['id']
            if remember_me:
                ex = 30 * 24 * 60 * 60
                token = self.create_token(user_id, ex)
            else:
                ex = 24 * 60 * 60
                token = self.create_token(user_id, ex)
            # self.redis_add(token, user["id"])
            return token, user
        else:
            return None

    def redis_add(self, key, value):
        self.redis_con.set(key, value)

    def get_user_by_token(self, token):
        try:
            id = self.redis_con.get(token).decode("utf-8")
            user = self.get_user_by_id(id)
            if user:
                return user
            else:
                return None
        except:
            return None

    def get_user_by_id(self, id):
        try:
            self.postgre_cur.execute(
                "SELECT * FROM users WHERE id=%s",
                (str(id),))
            user = self.postgre_cur.fetchone()
            if user:
                return dict(user)
            else:
                return None
        except:
            return None

    def get_postgres_con(self):
        return self.postgre_con

    def add_avatar(self, avatar, user_id):
        self.postgre_cur.execute("SELECT avatar FROM users WHERE id=%s", (user_id,))
        old_image = self.postgre_cur.fetchone()[0]

        if old_image != None:
            os.remove(os.path.join(UPLOAD_DIR_AVATAR, old_image))

        avatar.filename = user_id + Path(avatar.filename).suffix
        os.makedirs(UPLOAD_DIR_AVATAR, exist_ok=True)
        avatar_file_location = os.path.join(UPLOAD_DIR_AVATAR, avatar.filename)
        with open(avatar_file_location, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)

        self.postgre_cur.execute(
            "UPDATE users SET avatar = %s WHERE id = %s",
            (avatar.filename, user_id))
        self.postgre_con.commit()

    def put_avatar(self, avatar, user_id):
        avatar.filename = user_id + Path(avatar.filename).suffix
        os.makedirs(UPLOAD_DIR_AVATAR, exist_ok=True)
        avatar_file_location = os.path.join(UPLOAD_DIR_AVATAR, avatar.filename)
        with open(avatar_file_location, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)

        self.postgre_cur.execute(
            "UPDATE users SET avatar = %s WHERE id = %s IF NOT EXISTS",
            (avatar.filename, user_id))
        self.postgre_con.commit()

    def add_address(self, name, lon, lat):
        self.postgre_cur.execute(
            "INSERT INTO addresses (name, lon, lat) VALUES (%s, %s, %s) RETURNING id",
            (name, lon, lat)
        )
        address_id = self.postgre_cur.fetchone()[0]
        self.postgre_con.commit()
        return address_id

    def get_address(self, address_id):
        self.postgre_cur.execute(
            "SELECT * FROM addresses WHERE id=%s",
            (address_id,)
        )
        address = self.postgre_cur.fetchone()
        if address:
            return address
        else:
            return None

    def delete_address(self, address_id):
        self.postgre_cur.execute(
            "DELETE FROM addresses WHERE id=%s",
            (address_id,)
        )
        self.postgre_con.commit()
        return True

    def get_all_addresses(self):
        self.postgre_cur.execute(
            "SELECT id, name, lon, lat FROM addresses"
        )
        addresses = self.postgre_cur.fetchall()

        result = []
        for address in addresses:
            result.append({
                "id": address[0],
                "name": address[1],
                "lon": address[2],
                "lat": address[3]
            })

        return result

    def add_building(self, name, img, addr_id, year_from, year_to):
        random_filename = f"{uuid.uuid4()}{Path(img.filename).suffix}"
        os.makedirs(UPLOAD_DIR_BUILDINGS, exist_ok=True)
        img_file_location = os.path.join(UPLOAD_DIR_BUILDINGS, random_filename)
        with open(img_file_location, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

        self.postgre_cur.execute(
            "INSERT INTO buildings (name, img, addr_id, t_from, t_to) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (name, random_filename, str(addr_id), year_from, year_to)
        )
        building_id = self.postgre_cur.fetchone()[0]
        self.postgre_con.commit()
        return building_id

    def get_building(self, building_id):
        self.postgre_cur.execute(
            "SELECT * FROM buildings WHERE id=%s",
            (building_id,)
        )
        building = self.postgre_cur.fetchone()
        if building:
            return building
        else:
            return None

    def get_buildings_by_address(self, address_id):
        self.postgre_cur.execute(
            "SELECT id, name, img, t_from, t_to FROM buildings WHERE addr_id=%s",
            (address_id,)
        )
        buildings = self.postgre_cur.fetchall()
        result = []
        for building in buildings:
            result.append({
                "id": building[0],
                "name": building[1],
                "img": building[2],
                "t_from": building[3],
                "t_to": building[4],
                "address_id": address_id
            })

        return result

    def delete_building(self, building_id):
        self.postgre_cur.execute(
            "SELECT img FROM buildings WHERE id=%s",
            (building_id,)
        )
        result = self.postgre_cur.fetchone()

        if result and result[0]:
            img_name = result[0]
            try:
                img_path = os.path.join(UPLOAD_DIR_BUILDINGS, img_name)
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception as e:
                print(f"Ошибка при удалении файла изображения здания: {str(e)}")

        self.postgre_cur.execute(
            "DELETE FROM buildings WHERE id=%s",
            (building_id,)
        )
        self.postgre_con.commit()
        return True

    def update_building(self, building_id, name=None, t_from=None, t_to=None, img=None):
        self.postgre_cur.execute(
            "SELECT img, name, addr_id, t_from, t_to FROM buildings WHERE id=%s",
            (building_id,)
        )
        result = self.postgre_cur.fetchone()

        current_img_name, current_name, current_addr_id, current_t_from, current_t_to = result

        img_filename = current_img_name
        if img:
            try:
                current_img_path = os.path.join(UPLOAD_DIR_BUILDINGS, current_img_name)
                if os.path.exists(current_img_path):
                    os.remove(current_img_path)
            except Exception as e:
                print(f"Ошибка при удалении старого изображения: {str(e)}")

            random_filename = f"{uuid.uuid4()}{Path(img.filename).suffix}"
            os.makedirs(UPLOAD_DIR_BUILDINGS, exist_ok=True)
            img_file_location = os.path.join(UPLOAD_DIR_BUILDINGS, random_filename)
            with open(img_file_location, "wb") as buffer:
                shutil.copyfileobj(img.file, buffer)
            img_filename = random_filename

        new_name = name if name is not None else current_name
        new_t_from = t_from if t_from is not None else current_t_from
        new_t_to = t_to if t_to is not None else current_t_to

        self.postgre_cur.execute(
            "UPDATE buildings SET img=%s, name=%s, t_from=%s, t_to=%s WHERE id=%s",
            (img_filename, new_name, new_t_from, new_t_to, building_id)
        )
        self.postgre_con.commit()
        return True

    def add_floor(self, img, floor_number, building_id):
        random_filename = f"{uuid.uuid4()}{Path(img.filename).suffix}"
        os.makedirs(UPLOAD_DIR_FLOORS, exist_ok=True)
        img_file_location = os.path.join(UPLOAD_DIR_FLOORS, random_filename)
        with open(img_file_location, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

        self.postgre_cur.execute(
            "INSERT INTO floors (img, number, building_id) VALUES (%s, %s, %s) RETURNING id",
            (random_filename, floor_number, str(building_id))
        )
        floor_id = self.postgre_cur.fetchone()[0]
        self.postgre_con.commit()
        return floor_id

    def get_floor(self, floor_id):
        self.postgre_cur.execute(
            "SELECT * FROM floors WHERE id=%s",
            (floor_id,)
        )
        floor = self.postgre_cur.fetchone()
        if floor:
            return floor
        else:
            return None

    def get_floors_by_building(self, building_id):
        self.postgre_cur.execute(
            "SELECT id, number, img FROM floors WHERE building_id=%s ORDER BY number",
            (building_id,)
        )
        floors = self.postgre_cur.fetchall()

        result = []
        for floor in floors:
            result.append({
                "id": floor[0],
                "number": floor[1],
                "img": floor[2],
                "building_id": building_id
            })

        return result

    def update_floor(self, floor_id, floor_number=None, building_id=None, img=None):
        self.postgre_cur.execute(
            "SELECT img, number, building_id FROM floors WHERE id=%s",
            (floor_id,)
        )
        result = self.postgre_cur.fetchone()

        if not result:
            return False

        current_img_name, current_floor_number, current_building_id = result

        img_filename = current_img_name
        if img:
            try:
                current_img_path = os.path.join(UPLOAD_DIR_FLOORS, current_img_name)
                if os.path.exists(current_img_path):
                    os.remove(current_img_path)
            except Exception as e:
                print(f"Ошибка при удалении старого изображения: {str(e)}")

            random_filename = f"{uuid.uuid4()}{Path(img.filename).suffix}"
            os.makedirs(UPLOAD_DIR_FLOORS, exist_ok=True)
            img_file_location = os.path.join(UPLOAD_DIR_FLOORS, random_filename)
            with open(img_file_location, "wb") as buffer:
                shutil.copyfileobj(img.file, buffer)
            img_filename = random_filename

        new_floor_number = floor_number if floor_number is not None else current_floor_number
        new_building_id = building_id if building_id is not None else current_building_id

        if building_id is not None and building_id != current_building_id:
            if not self.check_if_building_exists(building_id):
                return False

        self.postgre_cur.execute(
            "UPDATE floors SET img=%s, number=%s, building_id=%s WHERE id=%s",
            (img_filename, new_floor_number, new_building_id, floor_id)
        )
        self.postgre_con.commit()
        return True

    def delete_floor(self, floor_id):
        self.postgre_cur.execute(
            "SELECT img FROM floors WHERE id=%s",
            (floor_id,)
        )
        result = self.postgre_cur.fetchone()

        if result and result[0]:
            img_name = result[0]
            try:
                img_path = os.path.join(UPLOAD_DIR_FLOORS, img_name)
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception as e:
                print(f"Ошибка при удалении файла изображения этажа: {str(e)}")

        # Удаляем запись из базы данных
        self.postgre_cur.execute(
            "DELETE FROM floors WHERE id=%s",
            (floor_id,)
        )
        self.postgre_con.commit()
        return True


    def add_documents(self, documents, user_id):
        os.makedirs(UPLOAD_DIR_DOCS, exist_ok=True)

        for document in documents:
            # Генерация имени файла с добавлением user_id
            document.filename = str(uuid.uuid4()) + Path(document.filename).suffix
            document_file_location = os.path.join(UPLOAD_DIR_DOCS, document.filename)

            with open(document_file_location, "wb") as buffer: # файл на диск
                shutil.copyfileobj(document.file, buffer)

            # Сохранение пути к файлу в базе данных
            self.postgre_cur.execute(
                "INSERT INTO docs (user_id, filename) VALUES (%s, %s)",
                (user_id, document.filename))

            self.postgre_cur.execute(
                "UPDATE users SET verified = FALSE WHERE id = %s",
                (user_id, ))
            # если документы обновлены, ставим флаг верификации на False. Далее админ верифицирует вручную

            self.postgre_con.commit()

    def get_all_users(self, limit, offset):
        self.postgre_cur.execute(
            "SELECT * FROM users WHERE role!= 'SUPER_ADMIN' and role!= 'ADMIN' ORDER BY login LIMIT %s OFFSET %s", (limit, offset))
        data = self.postgre_cur.fetchall()
        users = [dict(user) for user in data]
        for user in users:
            user.pop("password_hash", None)
        return users
    
    def check_if_address_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM addresses WHERE id=%s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_building_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM buildings WHERE id=%s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0

    def check_if_floor_exists_in_building(self, floor_number, building_id):
        self.postgre_cur.execute(
            "SELECT COUNT(*) FROM floors WHERE number=%s AND building_id=%s LIMIT 1",
            (floor_number, building_id)
        )
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_floor_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM floors WHERE id=%s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0

    def add_group(self, owner_id, user_logins, group_name):
        try:
            # получаем id по токену прям тут чтобы не ходить в БД дважды (пока не надо)
            '''self.postgre_cur.execute("SELECT id FROM users WHERE login=%s", (owner_id,))
            owner_id = self.postgre_cur.fetchone()[0]'''

            self.postgre_cur.execute(
                "INSERT INTO groups (name, owner) VALUES (%s, %s)",
                (group_name, owner_id))

            self.postgre_cur.execute(
                "INSERT INTO groups (name, owner) VALUES (%s, %s) RETURNING id",
                (group_name, owner_id))
            group_id = self.postgre_cur.fetchone()[0]
            self.postgre_con.commit()

            for login in user_logins:
                self.postgre_cur.execute("SELECT id FROM users WHERE login=%s", (login,))
                user_id = self.postgre_cur.fetchone()[0]
                self.postgre_cur.execute(
                    "INSERT INTO groups_members (group_id, user_id) VALUES (%s, %s)",
                    (group_id, user_id))
                self.postgre_con.commit()

            return group_id
        except:
            return None

    def get_group_by_id(self, group_id):
        self.postgre_cur.execute(
            """SELECT json_build_object(
                'group_name', g.name,
                'group_owner', json_build_object(
                        'id', owner.id,
                        'role', owner.role,
                        'login', owner.login,
                        'name', owner.name,
                        'surname', owner.surname,
                        'second_name', owner.secondname,
                        'email', owner.email,
                        'contacts', owner.contacts
                    ),
                'members', COALESCE(json_agg(
                    json_build_object(
                        'id', members.id,
                        'role', members.role,
                        'login', members.login,
                        'name', members.name,
                        'surname', members.surname,
                        'second_name', members.secondname,
                        'email', members.email,
                        'contacts', members.contacts
                    )
                ) FILTER (WHERE members.id IS NOT NULL), '[]')
            ) AS group_info
            FROM groups g
            LEFT JOIN users owner ON g.owner = owner.id
            LEFT JOIN groups_members gm ON g.id = gm.group_id
            LEFT JOIN users members ON gm.user_id = members.id
            WHERE g.id = %s
            GROUP BY g.id, g.name, owner.id, owner.login;
            """
            ,
            (group_id,))
        group = self.postgre_cur.fetchone()
        if not group:
            return None
        group = json.dumps(group[0], ensure_ascii=False)
        return group

    def check_if_item_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM items WHERE id=%s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0
    
    def check_if_seat_exists(self, uuid):
        self.postgre_cur.execute("SELECT COUNT(*) FROM seats WHERE id=%s LIMIT 1", (uuid,))
        return self.postgre_cur.fetchone()[0] > 0

    def get_avatar_by_user_id(self, user_id):
        self.postgre_cur.execute(
            "SELECT avatar FROM users WHERE id=%s",
            (user_id,))
        avatar_path = self.postgre_cur.fetchone()
        return avatar_path

    def get_docs_by_user_id(self, user_id):
        self.postgre_cur.execute(
            "SELECT filename FROM docs WHERE user_id=%s",
            (user_id,))
        file_names = self.postgre_cur.fetchall()
        file_names = [dict(file_name) for file_name in file_names]
        return file_names

    def verify_user(self, UserId):
        self.postgre_cur.execute(
            "UPDATE users SET verified = TRUE WHERE id = %s",
            (UserId,))
        self.postgre_con.commit()
        return True

    def sign_out(self, token):
        if not self.redis_con.exists(token):
            return False
        try:
            self.redis_con.delete(token)
            return True
        except:
            return False

    def patch_user(self, new_user: UserPatch, user_id):
        update_fields = []
        values = []

        if new_user.role is not None:
            update_fields.append("role=%s")
            values.append(new_user.role)

        if new_user.login is not None:
            update_fields.append("login=%s")
            values.append(new_user.login)

        if new_user.name is not None:
            update_fields.append("name=%s")
            values.append(new_user.name)

        if new_user.surname is not None:
            update_fields.append("surname=%s")
            values.append(new_user.surname)

        if new_user.second_name is not None:
            update_fields.append("secondname=%s")
            values.append(new_user.second_name)

        if new_user.email is not None:
            update_fields.append("email=%s")
            values.append(new_user.email)

        if new_user.contacts is not None:
            update_fields.append("contacts=%s")
            values.append(new_user.contacts)

        # Всегда обновляем verified (по твоему коду)
        update_fields.append("verified=false")

        # Если нет полей для обновления, ничего не делаем
        if not update_fields:
            return None

        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id=%s RETURNING *"
        values.append(user_id)

        self.postgre_cur.execute(query, tuple(values))
        user_updated = self.postgre_cur.fetchone()
        self.postgre_con.commit()

        return dict(user_updated) if user_updated else None