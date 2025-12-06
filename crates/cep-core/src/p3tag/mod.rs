// crates/cep-core/src/p3tag/mod.rs

mod generated;
mod manual;
mod status;

// reexport
pub use manual::build_p3tag_from_normalized_json;
