-- db_schema_v1.sql (Draft)
-- PostgreSQL dialect

CREATE TABLE users (
  id           UUID PRIMARY KEY,
  username     VARCHAR(100) UNIQUE NOT NULL,
  display_name VARCHAR(200) NOT NULL,
  dept         VARCHAR(200),
  role         VARCHAR(50) NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TYPE lock_status_enum AS ENUM ('UNLOCKED', 'LOCKED');

CREATE TABLE files (
  id              UUID PRIMARY KEY,
  original_name   VARCHAR(500) NOT NULL,
  stored_path     VARCHAR(1000) NOT NULL,
  file_size       BIGINT NOT NULL,
  mime_type       VARCHAR(200),
  checksum_sha256 CHAR(64) NOT NULL,
  version         INT NOT NULL DEFAULT 1,
  parent_file_id  UUID NULL REFERENCES files(id),
  is_latest       BOOLEAN NOT NULL DEFAULT TRUE,
  lock_status     lock_status_enum NOT NULL DEFAULT 'UNLOCKED',
  locked_by       UUID NULL REFERENCES users(id),
  uploader_id     UUID NOT NULL REFERENCES users(id),
  created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
  expiry_date     DATE NULL,
  is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_files_latest ON files(is_latest);
CREATE INDEX idx_files_created_at ON files(created_at);

CREATE TABLE file_contexts (
  file_id       UUID NOT NULL REFERENCES files(id),
  project_code  VARCHAR(200),
  experiment_id VARCHAR(200),
  step_name     VARCHAR(200),
  tags          JSONB,
  PRIMARY KEY(file_id)
);

CREATE TABLE audit_logs (
  id          UUID PRIMARY KEY,
  actor_id    UUID REFERENCES users(id),
  action      VARCHAR(100) NOT NULL,
  file_id     UUID NULL REFERENCES files(id),
  meta        JSONB,
  created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_created_at ON audit_logs(created_at);
