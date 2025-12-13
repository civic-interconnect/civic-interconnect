// src/rust/cep-core/src/entity/mod.rs
pub mod generated;
pub mod identifiers;
pub mod manual;
pub mod normalizer;
pub mod resolver;

// Public surface of the entity module:
pub use identifiers::*;
pub use manual::*;

#[cfg(test)]
mod tests;
