CREATE TABLE users(
	username VARCHAR(20) NOT NULL,
	fullname VARCHAR(40) NOT NULL,
    email VARCHAR(40) NOT NULL,
    filename VARCHAR(64) NOT NULL,
    password VARCHAR(256) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(username)
);

CREATE TABLE posts(
    postid INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(64) NOT NULL,
    owner VARCHAR(20) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner) REFERENCES users(username)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE following(
    username1 VARCHAR(20) NOT NULL,
    username2 VARCHAR(20) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(username1, username2),
    FOREIGN KEY(username1) REFERENCES users(username)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(username2) REFERENCES users(username)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE comments(
    commentid INTEGER PRIMARY KEY AUTOINCREMENT,
    owner VARCHAR(20) NOT NULL,
    postid INTEGER NOT NULL,
    text VARCHAR(1024) NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner) REFERENCES users(username)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(postid) REFERENCES posts(postid)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE likes(
    owner VARCHAR(20) NOT NULL,
    postid INTEGER NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(owner, postid),
    FOREIGN KEY(owner) REFERENCES users(username)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(postid) REFERENCES posts(postid)
    ON UPDATE CASCADE ON DELETE CASCADE
);
