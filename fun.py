from typing import List

def sortColors(nums: List[int]) -> None:
    l = 0
    while l < len(nums):
        min_val = nums[l]
        min_index = l
        for i in range(l, len(nums)):
            num = nums[i]
            if num < min_val:
                min_val = num
                min_index = i
        nums[min_index] = nums[l]
        nums[l] = min_val
        l += 1                


colours = [2,0,2,1,1,0]
sortColors(colours)
print(colours)