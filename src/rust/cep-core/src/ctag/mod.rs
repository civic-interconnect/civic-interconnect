// src/rust/cep-core/src/ctag/mod.rs

mod generated;
mod manual;
mod status;

// reexport
pub use manual::build_ctag_from_normalized_json;
