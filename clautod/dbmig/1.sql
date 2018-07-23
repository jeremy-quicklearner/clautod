BEGIN TRANSACTION;

PRAGMA user_version = 1;

CREATE TABLE users (
    username        VARCHAR PRIMARY KEY UNIQUE NOT NULL,
    privilege_level INTEGER NOT NULL,
    password_salt   VARCHAR NOT NULL,
    password_hash   VARCHAR NOT NULL
);

INSERT INTO users VALUES (
    "admin",
    3,
    "1531632349514513",
    "f4ab435b196203868161a3ac12f007c4223f5e6638cb3e7a11ff211c44e76009"
);

COMMIT;