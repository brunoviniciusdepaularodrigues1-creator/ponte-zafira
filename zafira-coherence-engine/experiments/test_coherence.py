import sys
import os

# Add the project root to sys.path to allow imports from core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_loop import psi0_cycle

low_noise = psi0_cycle(E=0.5, steps=100)
high_noise = psi0_cycle(E=2.0, steps=100)

print("LOW:", low_noise[-1])
print("HIGH:", high_noise[-1])
