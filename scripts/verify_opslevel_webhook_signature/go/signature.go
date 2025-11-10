package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/http"
	"sort"
	"strings"
)

const ErrorMissingHeaderPattern = "missing header '%s'"

const (
	HeaderSignature  = "X-OpsLevel-Signature"
	HeaderTiming     = "X-OpsLevel-Timing"
	HeaderActionUUID = "X-OpsLevel-Action-Uuid"
)

// Search for OpsLevel signature
func GetSignatureFromHeader(headers http.Header) (string, error) {
	signature := headers.Get(HeaderSignature)

	if signature == "" {
		return "", fmt.Errorf(ErrorMissingHeaderPattern, HeaderSignature)
	}

	return signature, nil
}

// Build the content to be signed
func BuildContent(headers http.Header, additionalHeadersToKeep []string, body []byte) (string, error) {
	if headers.Get(HeaderTiming) == "" {
		return "", fmt.Errorf(ErrorMissingHeaderPattern, HeaderTiming)
	}

	// Build the headers for signature verification
	keys := []string{HeaderTiming} // Make sure we always have X-Opslevel-Timing in there
	// Adds X-OpsLevel-Action-Uuid from asynchronous action requests
	if headers.Get(HeaderActionUUID) != "" {
		keys = append(keys, HeaderActionUUID)
	}
	for _, additionalHeader := range additionalHeadersToKeep {
		keys = append(keys, additionalHeader)
	}
	sort.Strings(keys)

	// Create the header content portion
	headerContent := make([]string, 0, len(keys))
	for _, k := range keys {
		headerContent = append(headerContent, k+":"+headers.Get(k))
	}
	h := strings.Join(headerContent, ",")

	// Build content
	return fmt.Sprintf("%s+%s", h, string(body)), nil
}

// Verify that the content match the hmacSig.
func Verify(content string, hmacSig string, secret string) (string, bool) {
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(content))
	computedSig := "sha256=" + hex.EncodeToString(mac.Sum(nil))
	if computedSig != hmacSig {
		return computedSig, false
	}
	return computedSig, true
}
