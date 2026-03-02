-- This is a comment line
-- Another comment

function hello_world()
    print("Hello, World!")  -- inline comment
end

function table.insert(t, value)
    table.insert(t, value)  -- calling a function
end

local obj = {}
function obj:method()
    return self.value  -- return statement
end

-- Test numbers and operators
local x = 42
local y = 10 + 20 * 3
local is_true = (x > y) and (x ~= y)

-- Test keywords
if x > y then
    print("x is greater")
elseif x < y then
    print("x is less")
else
    print("x equals y")
end

for i = 1, 10 do
    print("Count: " .. i)
end

while x > 0 do
    x = x - 1
end

-- Test different function name patterns
function simple_function() end
function with_underscore_name() end
function table.nested.function() end
function object:method_name() end