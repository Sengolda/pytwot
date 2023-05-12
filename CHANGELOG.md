# pytwot (1.5.0-final)

### Changes

- changed property `Tweet.medias` to `Tweet.media` this is a **breaking change**
- changed method `StreamCnnection.is_close()` to `StreamConnection.is_closed()` this is a **breaking change**
- changed classmethod `Stream.sample_stream()` to `Stream.sample()` this is a **breaking change** 
- Client's `sleep_after_ratelimit` parameter renamed to `handle_ratelimits` and set it to `True` by default, this is a **breaking change**

### Improved Documentation

- Fixed alot of gramatical errors
