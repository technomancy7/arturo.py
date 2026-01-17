# arturo.py
A simple wrapper around the arturo scripting language.
Requires the arturo binary to be findable in PATH.

## todo
- [ ] python function calling from arturo
- [ ] functions to extend the base template programatically
- [ ] ???

## example
```py
code = """
signal "test"
signal.key: "user" "chat"
print "hey there world"
print "all output is captured"
setv "testkey" "completed the test"
"""

a = Arturo()
output = a.version()
print("Output received:\n", output) # arturo 0.10.0 Arizona Bark (amd64/linux)

output = a.code(example)
print("Example test received:\n", output) # {'signals': ['message->test', 'user->chat'], 'vars': {'testkey': 'completed the test'}, 'output': 'hey there world\nall output is captured'}
```
