package main

import (
	"fmt"
	"math/rand"
	"os"
	"strconv"
)

func generate(seed int64, percentage float32, width int, wreckageIter int, cavesIter int) [][]rune {
	grid, onlist := randomNoise(seed, percentage, width)
	grid = runAutomata(grid, onlist, wreckageIter, cavesIter)
	grid = removeSmallIslandsAndHoles(grid)
	result := toString(grid)
	return result
}

func main() {
	if(len(os.Args) < 6){
		fmt.Println("Usage: go run wreckageSparseMatrix.go [seed] [fill percentage] [width] [wreckage iterations] [caves iterations]")
		return
	}
	// theGrid := generate(76687654, 0.55, 500, 20, 10)
	args := os.Args[1:]
	seed,_ := strconv.ParseInt(args[0],10,64)
	percent64,_ := strconv.ParseFloat(args[1],32)
	percentage := float32(percent64)
	width,_ := strconv.Atoi(args[2])
	wreckageIter,_ := strconv.Atoi(args[3])
	cavesIter,_ := strconv.Atoi(args[4])
	theGrid := generate(seed,percentage,width,wreckageIter,cavesIter)
	for i := range theGrid {
		for j := range theGrid[i] {
			fmt.Printf(string(theGrid[i][j]))
		}
		// fmt.Printf("%d", i);
		fmt.Println()
	}
}

func randomNoise(seed int64, percentage float32, width int) ([][]int, [][]int) {
	rand.Seed(seed)
	var result [][]int
	var onlist [][]int
	for i := 0; i < width; i++ {
		result = append(result, []int{})
		for j := 0; j < width; j++ {
			if rand.Float32() <= percentage {
				result[i] = append(result[i], 1)
				onlist = append(onlist, []int{i, j})
			} else {
				result[i] = append(result[i], 0)
			}
		}
	}
	return result, onlist
}

func neighbors(x int, y int, width int) [][]int {
	likelyResults := [][]int{
		[]int{x - 1, y + 1}, []int{x, y + 1}, []int{x + 1, y + 1},
		[]int{x - 1, y}, []int{x + 1, y},
		[]int{x - 1, y - 1}, []int{x, y - 1}, []int{x + 1, y - 1},
	}
	results := [][]int{}
	//check for in bounds
	for i := 0; i < 8; i++ {
		if likelyResults[i][0] >= 0 && likelyResults[i][0] < width && likelyResults[i][1] >= 0 && likelyResults[i][1] < width {
			results = append(results, likelyResults[i])
		}
	}
	return results
}

func contains(list []int, num int) bool {
	for i := range list {
		if list[i] == num {
			return true
		}
	}
	return false
}

func copyOf(grid [][]int) [][]int {
	result := [][]int{}
	for i := 0; i < len(grid); i++ {
		result = append(result, []int{})
		for j := 0; j < len(grid[i]); j++ {
			result[i] = append(result[i], grid[i][j])
		}
	}
	return result
}
func runAutomata(grid [][]int, onlist [][]int, wreckageIter int, cavesIter int) [][]int {
	// first:Wreckage (B5678/S35678) for 20 generations
	width := len(grid)
	birth := []int{5,6,7,8}
	survival := []int{3,5,6,7,8}
	// birth := []int{3}
	// survival := []int{2,3}
	for iteration := 0; iteration < wreckageIter; iteration++ {
		fmt.Println(iteration)
		prevGrid := copyOf(grid)
		newOnlist := [][]int{}
		for _, cell := range onlist {
			i := cell[0]
			j := cell[1]
			neighborCount := 0
			//get num neighbors active
			myNeighbors := neighbors(i, j, width)
			for _, neighbor := range myNeighbors {
				if prevGrid[neighbor[0]][neighbor[1]] == 0 {
					neighborsNeighborCount := 0
					neighborsNeighbors := neighbors(neighbor[0], neighbor[1], width)
					for _, neighborsNeighbor := range neighborsNeighbors {
						if prevGrid[neighborsNeighbor[0]][neighborsNeighbor[1]] == 1 {
							neighborsNeighborCount++
						}
					}
					if contains(birth, neighborsNeighborCount) { //new cell born
						grid[neighbor[0]][neighbor[1]] = 1
						prevGrid[neighbor[0]][neighbor[1]] = 3                         //mark as already reached to reduce redundant searches
						newOnlist = append(newOnlist, []int{neighbor[0], neighbor[1]}) //add this cell to onlist
					}
				} else if prevGrid[neighbor[0]][neighbor[1]] == 1 {
					neighborCount++
				}
			}
			if contains(survival, neighborCount) { //old cell survived to next generation
				grid[i][j] = 1
				newOnlist = append(newOnlist, []int{i, j})
			} else {
				grid[i][j] = 0 //old cell died
			}
		}
		onlist = newOnlist
	}
	// second:Caves (B5678/S45678) for 10 generations
	survival[0] = 4
	for iteration := 0; iteration < cavesIter; iteration++ {
		fmt.Println(iteration)
		// fmt.Println(len(onlist))
		prevGrid := copyOf(grid)
		newOnlist := [][]int{}
		for _, cell := range onlist {
			i := cell[0]
			j := cell[1]
			neighborCount := 0
			//get num neighbors active
			myNeighbors := neighbors(i, j, width)
			for _, neighbor := range myNeighbors {
				if prevGrid[neighbor[0]][neighbor[1]] == 0 {
					neighborsNeighborCount := 0
					neighborsNeighbors := neighbors(neighbor[0], neighbor[1], width)
					for _, neighborsNeighbor := range neighborsNeighbors {
						if prevGrid[neighborsNeighbor[0]][neighborsNeighbor[1]] == 1 {
							neighborsNeighborCount++
						}
					}
					if contains(birth, neighborsNeighborCount) { //new cell born
						grid[neighbor[0]][neighbor[1]] = 1
						prevGrid[neighbor[0]][neighbor[1]] = 3                         //mark as already reached to reduce redundant searches
						newOnlist = append(newOnlist, []int{neighbor[0], neighbor[1]}) //add this cell to onlist
					}
				} else if prevGrid[neighbor[0]][neighbor[1]] == 1 {
					neighborCount++
				}
			}
			if contains(survival, neighborCount) { //old cell survived to next generation
				grid[i][j] = 1
				newOnlist = append(newOnlist, []int{i, j})
			} else {
				grid[i][j] = 0 //old cell died
			}
		}
		onlist = newOnlist
	}
	return grid
}

func containsGrid(list [][]int, num []int) bool {
	for i := range list {
		if list[i][0] == num[0] && list[i][1] == num[1] {
			return true
		}
	}
	return false
}

func removeSmallIslandsAndHoles(grid [][]int) [][]int {
	result := [][]int{}
	width := len(grid)
	for i := 0; i < width; i++ {
		result = append(result, []int{})
		for j := 0; j < width; j++ {
			result[i] = append(result[i], 0)
		}
	}
	howSmallToRemoveIsland := 180
	howSmallToRemoveHole := 180
	//flood fill
	for i := range grid {
		for j := range grid[i] {
			if grid[i][j] == 0 || grid[i][j] == 1 { //new chunk
				original := grid[i][j]
				q := [][]int{[]int{i, j}}
				blob := [][]int{[]int{i, j}}
				for len(q) > 0 {
					x, y := q[0][0], q[0][1]
					q = q[1:]
					for _, neighbor := range neighbors(x, y, width) {
						if grid[neighbor[0]][neighbor[1]] == grid[x][y] {
							if !containsGrid(q, neighbor) {
								q = append(q, neighbor)
								blob = append(blob, neighbor)
							}
						}
					}
					grid[x][y] = 3 //mark this cell as done
				}
				// fmt.Println(len(blob))
				if original == 0 {
					if len(blob) <= howSmallToRemoveHole {
						for _, cell := range blob {
							result[cell[0]][cell[1]] = 2
						}
					} else {
						for _, cell := range blob {
							result[cell[0]][cell[1]] = 0
						}
					}
				} else {
					if len(blob) <= howSmallToRemoveIsland {
						for _, cell := range blob {
							result[cell[0]][cell[1]] = 0
						}
					} else {
						for _, cell := range blob {
							result[cell[0]][cell[1]] = 1
						}
					}
				}
			}
		}
	}
	return result
}

func toString(grid [][]int) [][]rune {
	result := [][]rune{}
	for i := range grid {
		result = append(result, []rune{})
		for j := range grid[i] {
			if grid[i][j] == 0 {
				result[i] = append(result[i], ' ')
			} else if grid[i][j] == 1 {
				result[i] = append(result[i], '1')
			} else if grid[i][j] == 2 {
				result[i] = append(result[i], '2')
			} else if grid[i][j] == 3 {
				result[i] = append(result[i], '3')
			}
		}
	}
	return result
}
