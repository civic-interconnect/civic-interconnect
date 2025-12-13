// crates/cep-core/src/common/attestations.rs

use serde::de::{self, Deserialize, Deserializer};

pub fn deserialize_nonempty_vec<'de, D, T>(deserializer: D) -> Result<Vec<T>, D::Error>
where
    D: Deserializer<'de>,
    T: Deserialize<'de>,
{
    let v = Vec::<T>::deserialize(deserializer)?;
    if v.is_empty() {
        return Err(de::Error::custom(
            "attestations must contain at least 1 item",
        ));
    }
    Ok(v)
}
