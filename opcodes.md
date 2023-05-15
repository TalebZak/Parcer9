| Opcode | Operation      | 1st operand   | 2nd operand   | 3rd operand   | Comments                                                                                             |
|--------|----------------|---------------|---------------|---------------|-----------------------------------------------------------------------------------------------------|
| +0     | Assignment     | Source        | Return value  | Destination   | If Return value !=0 then copy value from RVR into Dest                                              |
| -0     | Modulo         | Dividend      | Divisor       | Remainder     | Remainder  Dividend % Divisor                                                                      |
| +1     | Addition       | Addendum1     | Addendum2     | Sum           | Sum  Add1 + Add2                                                                                   |
| -1     | Subtraction    | Minuend       | Subtrahend    | Difference    | Diff  Min – Sub                                                                                    |
| +2     | Multiplication | Multiplicand1 | Multiplicand2 | Product       | Prod  Mult1 * Mult2                                                                                |
| -2     | Division       | Dividend      | Divisor       | Quotient      | Quotient  Dividend / Divisor                                                                       |
| +3     | Function call  | ARsize        | Return address| Destination   | Sets up the AR (params set up before function call, SL always pointing to global EP = base of the stack), Destination is the start address of the function being called |
| -3     | Function return| Return value  | Not used      | Not used      | Copy value return value to RVR. If there is no return value, you can just return 0.                 |
| +4     | Equality       | Comparand1    | Comparand2    | Destination   | If Comp1 = Comp2 goto Dest                                                                          |
| -4     | Inequality     | Comparand1    | Comparand2    | Destination   | If Comp1 != Comp2 goto Dest                                                                         |
| +5     | GEQ            | Comparand1    | Comparand2    | Destination   | If Comp1 >= Comp2 goto Dest                                                                         |
| -5     | LT             | Comparand1    | Comparand2    | Destination   | If Comp1 < Comp2 goto Dest                                                                          |
| +6     | Read Array     | Element       | Array         | Index         | Destination Dest  Array[Index]                                                                     |
| -6     | Write Array    | Index         | Source        | Array         | Index Array[Index]  Source                                                                         |
| +7     | Loop increment & test| Index    | Comparand    | Destination   | If Index++ < Comp goto Dest                                                                          |
| -7     | NOT USED       |               |               |               |                                                                                                     |
| +8     | Input value    | Not used      | Not used      | Destination   | Dest  input                                                                                        |
| -8     | Output value   | Source        | Not used      | Not used      | Output Source                                                                                        |
| +9     | Stop execution | +9000000000 (halt) |         |               |                                                                                                     |
| -9     | Sets base for relative addressing | Val1       | Val2          | Val3            | BASE1  Val1
                                                                    BASE2  Val2
                                                                    BASE3  Val3                                                                   |
