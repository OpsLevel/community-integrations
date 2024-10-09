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

const (
	HeaderSignatureCanonical = "X-Opslevel-Signature"
	HeaderSignature          = "X-OpsLevel-Signature"
	HeaderTimingCanonical    = "X-Opslevel-Timing"
	HeaderTiming             = "X-OpsLevel-Timing"
)

// Search for OpsLevel signature
func GetSignatureFromHeader(headers http.Header) (string, error) {
	if headers[HeaderSignatureCanonical] == nil {
		return "", fmt.Errorf("missing header '%s'", HeaderSignatureCanonical)
	}
	return headers[HeaderSignatureCanonical][0], nil
}

// Build the content to be signed
func BuildContent(headers http.Header, additionalHeadersToKeep []string, body []byte) (string, error) {
	if headers[HeaderTimingCanonical] == nil {
		return "", fmt.Errorf("missing header '%s'", HeaderTimingCanonical)
	}

	// Build the headers for signature verification
	keys := append([]string{HeaderTiming}, additionalHeadersToKeep...) // Make sure we always have X-Opslevel-Timing in there
	sort.Strings(keys)

	// Create the header content portion
	headerContent := []string{}
	for _, k := range keys {
		headerContent = append(headerContent, k+":"+headers[http.CanonicalHeaderKey(k)][0])
	}
	h := strings.Join(headerContent, ",")

	// Build content
	return fmt.Sprintf("%s+%s", h, string(body[:])), nil
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
