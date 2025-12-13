// FFI Bindings for Entity Module

// File: rust/cep-core/src/ffi/entity_bindings.rs

use crate::entity::manual::build_entity_from_normalized_json;
use std::ffi::{CStr, CString};
use std::os::raw::c_char; // Import the main builder function

// FFI Example: A function that takes a JSON string (as a C pointer) and returns
// a result string (also as a C pointer).
#[unsafe(no_mangle)]
pub extern "C" fn build_entity_record_from_json(input_json_ptr: *const c_char) -> *mut c_char {
    // Safety check for null pointer
    if input_json_ptr.is_null() {
        return std::ptr::null_mut();
    }

    // Convert C pointer to Rust string slice
    let input_json = unsafe { CStr::from_ptr(input_json_ptr) }.to_str().unwrap();

    // Call the core business logic function
    let result_string = match build_entity_from_normalized_json(input_json) {
        Ok(s) => s,
        Err(e) => format!("{{\"error\": \"{}\"}}", e),
    };

    // Convert the result back to a CString and return the raw pointer
    CString::new(result_string).unwrap().into_raw()
}

// Memory management function (CRITICAL for FFI)
#[unsafe(no_mangle)]
pub extern "C" fn free_string(s: *mut c_char) {
    if s.is_null() {
        return;
    }
    unsafe {
        // Take ownership and immediately drop it to free the allocation.
        drop(CString::from_raw(s));
    }
}
