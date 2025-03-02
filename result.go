package main

func demo() int {
	y := 1
	x := y + ((y << 3) >> 2)
	x = x >> 2
	return x
}

func main() {
}
