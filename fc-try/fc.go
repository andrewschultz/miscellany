// go run fc.go

package main

import "fmt"
import "strings"
import "math/rand"
import "os"
import "bufio"
import "strconv"

    var done bool = false
    var cards = [][]int{}
    var foundation = []int{ 0, 0, 0, 0 }
    var spares = []int{ -1, -1, -1 ,-1 }
	var suit_str = []string{ "C", "d", "S", "h" }
	var card_str = []string{ "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K" }

func shiftCols(i int, j int) {
  if j == i {
    fmt.Println("Can't move row onto itself")
	return
  }
  if i < 0 || j < 0 { fmt.Println("Must be > 0.")
  return
  }
  if i > 7 || j > 7 { fmt.Println("Must be < 8.")
  return
  }
  fmt.Println(0, i, len(cards[i]) - 1, j, len(cards[j]) - 1,
    cards[i][len(cards[i])-1], toCard(cards[i][len(cards[i])-1]),
	cards[j][len(cards[j])-1], toCard(cards[j][len(cards[j])-1]))
  if canMove(cards[i][len(cards[i])-1], cards[j][len(cards[j])-1]) { 
    fmt.Println("Yay! Can move.")
  }
}

func canMove (i int, j int) bool {
  if i % 13 == 12 { return false }
  if j % 13 - i % 13 != 1 { return false }
  fmt.Println(j/13, i/13, (j/13+i/13), (j/13+i/13) % 2)
  return ((j / 13) + (i / 13)) % 2 == 1
}

func toCard(j int ) string {

  if j == -1 {
    return "--  "
  }
  ret := card_str[j % 13]
  if j%13 != 9 {
  ret = " " + ret
  }
  ret = ret + suit_str[j / 13]
  return ret
}

func maxCol( x [][]int ) int {
  temp := 0
  
  for count := 0; count < len(x); count++ {
  if len(x[count]) > temp {
  temp = len(x[count])
  }
  }
  return temp
}

func checkAutoFound() {
  this_time := true
  su := 0
  cc := 0
  cv := 0
  for this_time == true {
  this_time = false
  for i := 0; i < 8; i++ {
    cc = cards[i][len(cards[i])-1]
	cv = cc % 13
	su = cc / 13
	if foundation[su] == cv {
	  if foundation[(su+1)%4] >= cv - 2 && foundation[(su+3)%4] >= cv - 2 {
	  this_time = true
	  cards[i] = cards[i][:len(cards[i])-1]
	  foundation[su] = foundation[su] + 1
	  }
	}
    }
  }
}

func main() {
    // Create an empty slice of slices.

	foundation[0] = 0
	
	for i:= 0; i < 8; i++ {
	cards = append(cards, []int{})
	}

	list := rand.Perm(52)
	
	for i:= 0; i < 52; i++ {
	cards[i%8] = append(cards[i%8], list[i])
	
	}

	for done == false {

    for j := 0; j < maxCol(cards); j++ {
	for i := 0; i < 8; i++ {
	    if j >= len(cards[i]) {
		  fmt.Print("    ")
		} else {
		  fmt.Print(toCard(cards[i][j]), " ")
		}
	  }
	  fmt.Println()
	}
	fmt.Print("Foundation:")
	for i := 0; i < 4; i ++ {
	  fmt.Print(" ", foundation[i], suit_str[i])
	}
	fmt.Println()
	fmt.Print("Spares:")
	for i := 0; i < 4; i ++ {
	  fmt.Print(toCard(spares[i]))
	}
	fmt.Println()

    reader := bufio.NewReader(os.Stdin)
	
    fmt.Print("Enter text: ")
    text, _ := reader.ReadString('\n')
	
	i, err := strconv.Atoi(strings.TrimSpace(text))

    if err == nil && i <= 99 && i >= 10 {
	  shiftCols(i / 10 - 1, i % 10 - 1)
	} else {
	fmt.Println(err)
	}

	checkAutoFound()
	}

}