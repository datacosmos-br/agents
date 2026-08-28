package queue

import (
	"context"
	"errors"
)

var ErrRejected = errors.New("rejected")

type Sink interface {
	Write(context.Context, string) error
}

func Submit(sink Sink, value string) error {
	go func() {
		_ = sink.Write(context.Background(), value)
	}()
	return nil
}
