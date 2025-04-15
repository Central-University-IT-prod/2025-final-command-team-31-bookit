DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('SUPER_ADMIN', 'ADMIN', 'EMPLOYEE', 'GUEST');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE price_type AS ENUM ('fixed', 'perhour');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE category AS ENUM ('Еда', 'Оборудование');
EXCEPTION
    WHEN duplicate_object THEN null;

END $$;

CREATE TABLE IF NOT EXISTS users
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    role user_role NOT NULL,
    login text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    avatar text DEFAULT NULL,
    name text NOT NULL,
    secondname text DEFAULT NULL,
    surname text NOT NULL,
    email text DEFAULT NULL,
    contacts text DEFAULT NULL,
    verified boolean NOT NULL DEFAULT FALSE,
    qr_code text DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS addresses
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name text NOT NULL,
    lon double precision NOT NULL,
    lat double precision NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS buildings
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name text NOT NULL,
    img text DEFAULT NULL,
    addr_id uuid NOT NULL,
    t_from integer[] NOT NULL,
    t_to integer[] NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS floors
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    img text NOT NULL,
    number integer NOT NULL,
    building_id uuid NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS seats
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    floor_id uuid NOT NULL,
    posx double precision NOT NULL,
    posy double precision NOT NULL,
    name text NOT NULL,
    onlyempl boolean NOT NULL,
    price_g double precision NOT NULL,
    price_e double precision NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS bookings
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    seat_id uuid[] NOT NULL,
    t_from bigint NOT NULL,
    t_to bigint NOT NULL,
    price double precision NOT NULL,
    active boolean DEFAULT false,
    is_group boolean DEFAULT false,
    payed boolean DEFAULT false,
    parent uuid DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS groups
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    owner uuid NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS groups_members
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    group_id uuid NOT NULL,
    user_id uuid NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS docs
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    filename text NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS items
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name text NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    pricetype price_type NOT NULL,
    category category NOT NULL,
    image text DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS order_details
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    name text NOT NULL,
    booking_id uuid NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    pricetype price_type NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS book_items
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    booking_id uuid NOT NULL,
    seat_id uuid NOT NULL,
    t_from BIGINT NOT NULL,
    t_to BIGINT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS history
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    t_from BIGINT NOT NULL,
    t_to BIGINT NOT NULL,
    price BIGINT NOT NULL,
    description text NOT NULL,
    user_id uuid NOT NULL,
    seat_id uuid NOT NULL,
    group_users uuid[] DEFAULT NULL,
    group_id uuid DEFAULT NULL,
    items_id uuid DEFAULT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS suggestions
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    building_id uuid NOT NULL,
    txt text NOT NULL,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX IF NOT EXISTS login ON users(login);

INSERT INTO users (role, login, name, surname, secondname, password_hash, qr_code) VALUES ('SUPER_ADMIN', 'admin', 'admin', 'admin', 'admin', '$argon2id$v=19$m=65536,t=3,p=4$y4zeOrZM1mBqKJV5XM2Zhg$vZxSv2ez/GcpAiK6p+xQBv/1Nx6zcFAt6h7S93ndWzA', 'notvalidqr')
ON CONFLICT (login) DO NOTHING;