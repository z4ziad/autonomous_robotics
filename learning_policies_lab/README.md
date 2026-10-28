<p align="center">
  <img src="assets/logo.png" alt="CMU ECE Autonomous Robotics logo" width="420">
</p>
<h1 align="center">Autonomous Robotics II</h1>

<p align="center">
  Carnegie Mellon University · Electrical and Computer Engineering · Fall 2026<br>
  Instructor: Prof. Ziad Youssfi
</p>

---

For most of their history, robots have been programmed with explicit rules: e.g., move the arm x degrees to the left and z degrees down and close the gripper. That works on a factory line where nothing changes, but it fails the moment a part is out of place. Today, a robot can be taught a task in an afternoon of showing, recognize objects, follow instructions it was never shown, and keep improving on its own. This course is about how these learning methods or "policies" work and what their limits are.

The course examines three learning policy types:

- **Copying:** We record a person doing the task through the robot and train a model to reproduce the motion. This policy works, but the robot knows only what it has seen.
- **Generalizing:** We start from an LLM that has already learned from the Internet what things look like and what words mean, and attach the LLM to the robot's motors. Now the robot knows, for example, what a vial is before it has seen one, though it can still only move in ways it was shown.
- **Rewarding:** We let the robot try the task, tell it when it succeeded, and let it improve from its own attempts.

Today, the models for these robot learning policies are a hundred times smaller than just a couple of years ago. New robotic arms can be 3D printed to reduce cost. Thus, a team of students with a desktop PC can collect data, train open-source policies, and get real answers in a semester and find out which policies work best for which tasks.
