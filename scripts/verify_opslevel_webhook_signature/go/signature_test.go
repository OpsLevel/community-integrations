package main

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetSignatureFromHeader(t *testing.T) {
	headers := make(http.Header)
	_, err := GetSignatureFromHeader(headers)
	if err == nil {
		t.Error("expecting error")
	}

	headers[HeaderSignatureCanonical] = []string{"sha256=ab238ca1f60b94dbf50e7b237baf0dc93f02e4ff21736d549f9625d5300f962b"}
	hmacSig, _ := GetSignatureFromHeader(headers)
	if hmacSig != headers[HeaderSignatureCanonical][0] {
		t.Errorf("received sig is different, expected: '%s', received: '%s'", headers[HeaderSignatureCanonical][0], hmacSig)
	}
}
func TestGetContent(t *testing.T) {
	headers := make(http.Header)
	headers[HeaderTimingCanonical] = []string{"1726164245"}
	headers[HeaderSignatureCanonical] = []string{"sha256=ab238ca1f60b94dbf50e7b237baf0dc93f02e4ff21736d549f9625d5300f962b"}
	content, err := BuildContent(headers, nil, []byte{})

	expectedContent := fmt.Sprintf("%s:%s+", HeaderTiming, headers[HeaderTimingCanonical][0])
	if content != expectedContent {
		t.Errorf("content ('%s') is not what is expected ('%s')", content, expectedContent)
	}

	if err != nil {
		t.Errorf("there should be no error: %s", err)
	}
}

func TestGetContentMultiHeader(t *testing.T) {
	headers := make(http.Header)
	headers[HeaderTimingCanonical] = []string{"1726164245"}
	headers[HeaderSignatureCanonical] = []string{"sha256=ab238ca1f60b94dbf50e7b237baf0dc93f02e4ff21736d549f9625d5300f962b"}
	headers["Anotherheader-Signature"] = []string{"somevalue"}

	content, err := BuildContent(headers, []string{"Anotherheader-Signature"}, []byte{})

	expectedContent := fmt.Sprintf("Anotherheader-Signature:%s,%s:%s+", headers["Anotherheader-Signature"][0], HeaderTiming, headers[HeaderTimingCanonical][0])
	if content != expectedContent {
		t.Errorf("content ('%s') is not what is expected ('%s')", content, expectedContent)
	}

	if err != nil {
		t.Errorf("there should be no error: %s", err)
	}
}

func TestGetContentMultiHeaderWeirdLowercase(t *testing.T) {
	headers := make(http.Header)
	headers[HeaderTimingCanonical] = []string{"1726164245"}
	headers[HeaderSignatureCanonical] = []string{"sha256=ab238ca1f60b94dbf50e7b237baf0dc93f02e4ff21736d549f9625d5300f962b"}
	headers["Anotherheader-Signature"] = []string{"somevalue"}

	content, err := BuildContent(headers, []string{"anotherheader-Signature"}, []byte{})

	expectedContent := fmt.Sprintf("X-OpsLevel-Timing:%s,anotherheader-Signature:%s+", headers[HeaderTimingCanonical][0], headers["Anotherheader-Signature"][0])
	if content != expectedContent {
		t.Errorf("content ('%s') is not what is expected ('%s')", content, expectedContent)
	}

	if err != nil {
		t.Errorf("there should be no error: %s", err)
	}
}

func TestGetContentMultiHeaderMissing(t *testing.T) {
	headers := make(http.Header)
	headers[HeaderTimingCanonical] = []string{"1726164245"}
	headers[HeaderSignatureCanonical] = []string{"sha256=ab238ca1f60b94dbf50e7b237baf0dc93f02e4ff21736d549f9625d5300f962b"}
	headers["Anotherheader-Signature"] = []string{"somevalue"}

	// Test non-canonical header
	content, err := BuildContent(headers, nil, []byte{})

	expectedContent := fmt.Sprintf("X-OpsLevel-Timing:%s+", headers[HeaderTimingCanonical][0])
	if content != expectedContent {
		t.Errorf("content ('%s') is not what is expected ('%s')", content, expectedContent)
	}

	if err != nil {
		t.Errorf("there should be no error: %s", err)
	}
}

func TestVerify(t *testing.T) {
	headers := make(http.Header)
	headers[HeaderTimingCanonical] = []string{"1726164245"}
	headers[HeaderSignatureCanonical] = []string{"sha256=89649e9d66e0f48c8a6e67fc12197d68dbcb91710391555fcf3a59d8757bf63b"}
	content, err := BuildContent(headers, nil, []byte{})
	if err != nil {
		t.Fatalf("there should be no error on GetContent: %s", err)
	}
	hmacSig, err := GetSignatureFromHeader(headers)
	if err != nil {
		t.Fatalf("there should be no error on GetSignatureFromHeader: %s", err)
	}
	computedSig, _ := Verify(content, hmacSig, "somesecrethere")
	if computedSig != headers[HeaderSignatureCanonical][0] {
		t.Errorf("computed signature should be equal to header signature, expected: '%s', received: '%s'", computedSig, headers[HeaderSignatureCanonical][0])
	}
	if err != nil {
		t.Fatalf("there should be no error: %s", err)
	}
}

func TestGetContentErrors(t *testing.T) {
	headers := make(http.Header)
	headers[HeaderSignatureCanonical] = []string{"sha256=66eec7a940647ad571944363d4e044e6b39a687c1df8b0808f86b8a4ea085d6e"}

	content, err := BuildContent(headers, nil, []byte{})
	if err == nil {
		t.Errorf("should have received '%s' missing header errors", HeaderTimingCanonical)
	}
	if content != "" {
		t.Errorf("content should be '\"\"', got '%s'", content)
	}

	headers[HeaderTimingCanonical] = []string{"1726164245"}
	_, err = BuildContent(headers, nil, []byte{})
	if err != nil {
		t.Errorf("should not return any error: %s", err)
	}
}
