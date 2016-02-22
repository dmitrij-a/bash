drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  post_id text,
  post text
);