# SWARM Software Task Round 2021
This is my solution to SWARM Software Task Round 2021.

## Progress
I managed to solve all the levels.
I used file handling (2 txt files) to establish communication among bots.

## Approach
  - ### Path Planning :
      I used basic A* for path planning. I even explored RRT and it seemed like a pretty cool method. I tried an approach of combining RRT with A*, as in, RRT with a high step value gave checkpoints in the map, in just 50-100 iterations and A* was used to find path from checkpoint to next checkpoint (pretty fast as start and goal are not far away and there are mostly no obstacles along the way). It worked well but since its an iterative method, it will obviously give an approximate solution quickly rather than the optimal solution after taking relatively longer.
  - ### Coordination among bots? :
      I was told that we could use a centralized approach rather than actual coordination among bots. But the bots were running in parallel threads and we weren't allowed to change other files, such as ```api.py``` or ```controller.py``` (yeah I am not touching ```app.py```, thank you). So the approach I used was using two txt files, one as status indicator of the bots, other as achieved goals. It is created on its own if it doesnt exist in your folder. And its reset to proper format as soon as the mission is complete.

## Major Issues 
As of now there are two major issues, that I think I cannot fix, no matter how much time I am given.
  - ### Issue 1 : 
      Bot-bot collision is not taken care of, because to be honest, they are just points and what are the odds of collision, given the map is 200 X 200. Anyway precaution measures have been taken in goal assignment so as to try and avoid bot collision as much as possible.
  - ### Issue 2 :
      Yeah my code does random stuff sometimes, I honestly do not know why. Its the pain every fellow programmer has felt once in life atleast, right? No? I'm the only one? FFFFFF. So it works as expected 80% of the times and sometimes does unexpected stuff, I checked everything, I spent days finding the issue, but I couldnt find any, guess I'll just move on (to find newer issues).

## How to use
  - Well, follow this repository
  [TotALly NOt a RIckROll shhhh](https://github.com/shreyase99/SwarmSoftwareTask2021) (Trust me :slightly_smiling_face:).
  - Follow all the instructions there.
  - Next just copy paste the ```code.py``` code from this repository.
And you're good to go!

## Final Result
[Swarm Demo.mp4](https://user-images.githubusercontent.com/86613790/130007948-0622004d-86a2-4a17-b467-bf7ced68cdb0.mp4)

**POG**

