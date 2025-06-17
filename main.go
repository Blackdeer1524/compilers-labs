package main

import (
	"errors"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"os"
	"strconv"
)

func isPowerOfTwo(val int) bool {
	return val != 0 && (val&(val-1)) == 0
}

func findPowOfTwo(powOfTwo int) int {
	c := 0
	for powOfTwo != 1 {
		c++
		powOfTwo >>= 1
	}
	return c
}

var errNotLiteral = errors.New("not a literal")
var errNotPowTwo = errors.New("not a literal")

func getPowTwo(node ast.Node) (int, error) {
	right, ok := node.(*ast.BasicLit)
	if !ok || right.Kind != token.INT {
		return 0, errNotLiteral
	}
	value, err := strconv.Atoi(right.Value)
	if err != nil {
		panic("something went wrong: " + err.Error())
	}
	if !isPowerOfTwo(value) {
		return 0, errNotPowTwo
	}
	result := findPowOfTwo(value)
	return result, nil
}

func solve(file *ast.File) {
	ast.Inspect(file, func(node ast.Node) bool {
		v, ok := node.(*ast.BinaryExpr)
		if !ok {
			return true
		}

		left, okLeft := v.X.(*ast.BinaryExpr)
		if okLeft {
			v.X = &ast.ParenExpr{
				Lparen: 0,
				X:      left,
				Rparen: 0,
			}
		}

		right, okRight := v.Y.(*ast.BinaryExpr)
		if okRight {
			v.Y = &ast.ParenExpr{
				Lparen: 0,
				X:      right,
				Rparen: 0,
			}
		}

		if okRight {
			return true
		}

		powTwo, err := getPowTwo(v.Y)
		if err != nil {
			return true
		}

		if v.Op == token.MUL {
			v.Op = token.SHL
			v.Y = &ast.BasicLit{
				ValuePos: v.Y.Pos(),
				Kind:     token.INT,
				Value:    strconv.Itoa(powTwo),
			}
		} else if v.Op == token.QUO {
			v.Op = token.SHR
			v.Y = &ast.BasicLit{
				ValuePos: v.Y.Pos(),
				Kind:     token.INT,
				Value:    strconv.Itoa(powTwo),
			}
		}
		return true

	})
}

func main() {
	// if len(os.Args) != 2 {
	// 	fmt.Printf("usage: astprint <filename.go>\n")
	// 	return
	// }

	fname := os.Args[1] // "main.go"

	fset := token.NewFileSet()

	file, err := parser.ParseFile(
		fset,                 // данные об исходниках
		fname,                // имя файла с исходником программы
		nil,                  // пусть парсер сам загрузит исходник
		parser.ParseComments, // приказываем сохранять комментарии
	)
	if err != nil {
		panic(err)
	}

	solve(file)
	format.Node(os.Stdout, fset, file)
}
