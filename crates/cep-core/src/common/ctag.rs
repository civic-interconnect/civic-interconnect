use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ContextTag {
    /// Optional local identifier for the tag (UUID, stable key, etc.).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ctag_id: Option<String>,

    /// URI of the CTag type term in the vocabulary.
    pub tag_type_uri: String,

    /// Short code from the vocabulary (for example, "risk.flag.potential_shell").
    #[serde(skip_serializing_if = "Option::is_none")]
    pub code: Option<String>,

    /// Optional value or bucket associated with this tag.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<serde_json::Value>,

    /// Identifier of the system or agent that applied this tag.
    pub applied_by: String,

    /// RFC 3339 timestamp when the tag was applied.
    pub applied_at: String,

    /// Scope of the tag within the record.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub scope: Option<String>,

    /// Optional JSON Pointer or dot-path target when scope is field/relationship.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_path: Option<String>,

    /// Optional confidence in [0.0, 1.0].
    #[serde(skip_serializing_if = "Option::is_none")]
    pub confidence: Option<f64>,

    /// Optional identifier of the analysis run / model version.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_run_id: Option<String>,

    /// Optional human-readable note.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub note: Option<String>,

    /// Optional PROV activity URI this tag is associated with.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub prov_activity_uri: Option<String>,
}
