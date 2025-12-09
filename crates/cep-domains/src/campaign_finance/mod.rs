//! Campaign finance domain types.

pub mod candidate;
pub mod committee;
pub mod contribution;
pub mod donor;
pub mod expenditure;
pub mod transaction;

pub use candidate::CandidateRecord;
pub use committee::CommitteeRecord;
pub use contribution::ContributionRecord;
pub use donor::DonorRecord;
pub use expenditure::ExpenditureRecord;
pub use transaction::TransactionRecord;
