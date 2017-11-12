package main

import "fmt"
import "math/rand"
import "os"
import "bufio"

    var done bool = false
    var cards = [][]int{}
    var foundation = []int{ 0, 0, 0, 0 }
    var spares = []int{ -1, -1, -1 ,-1 }
	var suit_str = []string{ "C", "D", "S", "H" }
	var card_str = []string{ "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K" }

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
	
	fmt.Println(toCard(i))
	}

	for done == false {

	for i:= 0; i < 8; i++ {
	fmt.Println(cards[i])
	fmt.Println(len(cards[i]))
	}
	
	  for j := 0; j < 8; j++ {
	for i := 0; i < maxCol(cards); i++ {
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
    fmt.Print(text)
	checkAutoFound()
	}

}