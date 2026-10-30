CREATE TABLE processed_events (
  logical_consumer text NOT NULL,
  event_id text NOT NULL,
  PRIMARY KEY (logical_consumer, event_id)
);
CREATE TABLE account_points (
  account_id bigint PRIMARY KEY,
  points int NOT NULL
);
