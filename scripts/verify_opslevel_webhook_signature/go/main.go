package main

import (
	"fmt"
	"io"
	"net/http"
)

var (
	secret string = "OpslevelWebhookSecret"
)

func main() {
	http.HandleFunc("/webhook", func(w http.ResponseWriter, r *http.Request) {
		hmacSig, err := GetSignatureFromHeader(r.Header)
		if err != nil {
			panic(err)
		}
		b, err := io.ReadAll(r.Body)
		if err != nil {
			panic(err)
		}

		content, err := BuildContent(r.Header, nil, b)
		if err != nil {
			panic(err)
		}
		computedSig, match := Verify(content, hmacSig, secret)
		if !match {
			fmt.Printf("Signature does _not_ match!\n")
		} else {
			fmt.Printf("Signature match!\n")
		}
		fmt.Printf("Signature received in header: '%s'\n", hmacSig)
		fmt.Printf("Signature computed from payload: '%s'\n", computedSig)
		fmt.Printf("Pyaload content: '%s'\n", content)
	})

	fmt.Println("Server listening on http://localhost:8080/webhook")
	fmt.Println("Execute this for testing\n\ncurl -H 'X-Opslevel-Timing: 123456' -H 'X-Opslevel-Signature: sha256=ee9eac178fe5cd260ff1d6f9fedcc409c6389ea5718ec44c8e266c6128770233' localhost:8080/webhook")
	http.ListenAndServe(":8080", nil)
}
