// go run fc.go

package main

import "fmt"
import "strings"
import "math/rand"
import "os"
import "bufio"
import "strconv"
import "regexp"

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
  index := len(cards[i]) - 1
  cardsMove := 1
  keepgoing := true
  
  if len(cards[i]) == 0 {
    fmt.Println("Nothing to move.")
  }
  
  if len(cards[j]) == 0 {
    md := maxdump() / 2
	for keepgoing {
	  keepgoing = false
	  if (i > 0) && (canMove(cards[i][index], cards[i][index-1])) {
	    index = index - 1
		cardsMove = cardsMove + 1
		keepgoing = true
	  }
	  }
	  if cardsMove > md {
	    fmt.Println("Too many cards to move, too little dump space:", cardsMove, "vs", md)
		return
	  }
	  
	cards[j] = append(cards[j], (cards[i][len(cards[i])-cardsMove:])...)
	cards[i] = cards[i][:len(cards[i])-cardsMove]
	return
  } else {
  for keepgoing {
    if canMove(cards[i][index], cards[j][len(cards[j])-1]) { 
	  if cardsMove > maxdump() {
	    fmt.Println("Tried to move ", cardsMove, " but can only move ", maxdump())
		return
	  }
	  cards[j] = append(cards[j], (cards[i][len(cards[i])-cardsMove:])...)
	  cards[i] = cards[i][:len(cards[i])-cardsMove]	
	  return
	}
	keepgoing = (index > 0) && (canMove(cards[i][index], cards[i][index-1]))
	index = index - 1
	cardsMove = cardsMove + 1
	//fmt.Println("Match didn't work, trying for ", toCard(cards[i][index]), " onto ", toCard(cards[j][len(cards[j])-1]))
  }
  }
  //fmt.Println(cardsMove)
  fmt.Println("Those don't match up.")
}

func maxdump() int {
  exponent := 1
  mantissa := 1
  
  for i:=0; i < 8; i++ {
    if len(cards[i]) == 0 {
	  exponent = exponent * 2
	}
  }
  for i:=0; i < 3; i++ {
    if spares[i] == -1 {
	  mantissa = mantissa + 1
	}
  }
  //fmt.Println(exponent, mantissa, exponent * mantissa)
  return int (exponent * mantissa);
}

func canMove (i int, j int) bool {
  if i % 13 == 12 { return false }
  if j % 13 - i % 13 != 1 { return false }
  //fmt.Println(j/13, i/13, (j/13+i/13), (j/13+i/13) % 2)
  return ((j / 13) + (i / 13)) % 2 == 1
}

func toCard(j int ) string {

  if j == -1 {
    return "-- "
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
    if len(cards[i]) == 0 {
	  continue
	}
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

	for i := 0; i < 8; i++ {
	  fmt.Print("  ", i+1 , " ")
	}
	fmt.Println()

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
	fmt.Println("Can shift ", maxdump(), " cards at once")

    reader := bufio.NewReader(os.Stdin)
	
    fmt.Print("Enter text: ")
    text, _ := reader.ReadString('\n')
	
	i, err := strconv.Atoi(strings.TrimSpace(text))
	
	match1, _ := regexp.MatchString("^[1-8][a-d]$", strings.TrimSpace(text))
	match2, _ := regexp.MatchString("^[a-d][1-8]$", strings.TrimSpace(text))

    if err == nil && i <= 99 && i >= 10 {
	  shiftCols(i / 10 - 1, i % 10 - 1)
	  continue
	} else if match1 {
	y := int(text[1]) - 97
	x := int(text[0]) - 49
	fmt.Println("to spares: col ", x+1, " to space ", y+1)
	if spares[y] != -1 {
	  fmt.Println("Space ", y+1, " is full.")
	  continue
	}
	if len(cards[x]) == 0 {
	  fmt.Println("Col ", x+1, " is empty.")
	  continue
	}
	spares[y] = cards[x][len(cards[x])-1]
	cards[x] = cards[x][:len(cards[x])-1]
	fmt.Println("successful")
	} else if match2 {
	y := int(text[1]) - 49
	x := int(text[0]) - 97
	fmt.Println("from spares: space ", x+1, " to col ", y+1)
	if spares[x] == -1 {
	  fmt.Println("space ", x+1, " is empty.")
	  continue
	}
	if ((len(cards[y]) > 0) && (!canMove(spares[x], cards[y][len(cards[y])-1]))) {
	  fmt.Println("space ", x+1, " doesn't match with col ", y+1)
	  continue
	}
    cards[y] = append(cards[y], spares[x])
    spares[x] = -1
	fmt.Println("successful")
	} else {
	fmt.Println(err)
	}

	checkAutoFound()
	}

}