OPENQASM 2.0;
include "qelib1.inc";
gate ccircuit_798 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-0.9272952180016122,0,0) q1; cx q0,q1; u(0.9272952180016122,0,0) q1; }
gate ccircuit_807 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-1.8545904360032244,0,0) q1; cx q0,q1; u(1.8545904360032244,0,0) q1; }
gate ccircuit_816 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-3.7091808720064487,0,0) q1; cx q0,q1; u(3.7091808720064487,0,0) q1; }
gate ccircuit_825 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-7.4183617440128975,0,0) q1; cx q0,q1; u(7.4183617440128975,0,0) q1; }
gate ccircuit_834 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-14.836723488025795,0,0) q1; cx q0,q1; u(14.836723488025795,0,0) q1; }
gate ccircuit_843 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-29.67344697605159,0,0) q1; cx q0,q1; u(29.67344697605159,0,0) q1; }
gate ccircuit_852 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-59.34689395210318,0,0) q1; cx q0,q1; u(59.34689395210318,0,0) q1; }
gate ccircuit_861 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-118.69378790420636,0,0) q1; cx q0,q1; u(118.69378790420636,0,0) q1; }
gate ccircuit_870 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-237.38757580841272,0,0) q1; cx q0,q1; u(237.38757580841272,0,0) q1; }
gate ccircuit_879 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-474.77515161682544,0,0) q1; cx q0,q1; u(474.77515161682544,0,0) q1; }
gate ccircuit_888 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-949.5503032336509,0,0) q1; cx q0,q1; u(949.5503032336509,0,0) q1; }
gate ccircuit_897 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-1899.1006064673018,0,0) q1; cx q0,q1; u(1899.1006064673018,0,0) q1; }
gate ccircuit_906 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-3798.2012129346035,0,0) q1; cx q0,q1; u(3798.2012129346035,0,0) q1; }
gate ccircuit_915 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-7596.402425869207,0,0) q1; cx q0,q1; u(7596.402425869207,0,0) q1; }
gate ccircuit_924 q0,q1 { p(0) q0; p(0) q1; cx q0,q1; u(-15192.804851738414,0,0) q1; cx q0,q1; u(15192.804851738414,0,0) q1; }
gate gate_IQFT_dg q0,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14 { h q0; cp(-pi/2) q1,q0; h q1; cp(-pi/4) q2,q0; cp(-pi/2) q2,q1; h q2; cp(-pi/8) q3,q0; cp(-pi/4) q3,q1; cp(-pi/2) q3,q2; h q3; cp(-pi/16) q4,q0; cp(-pi/8) q4,q1; cp(-pi/4) q4,q2; cp(-pi/2) q4,q3; h q4; cp(-pi/32) q5,q0; cp(-pi/16) q5,q1; cp(-pi/8) q5,q2; cp(-pi/4) q5,q3; cp(-pi/2) q5,q4; h q5; cp(-pi/64) q6,q0; cp(-pi/32) q6,q1; cp(-pi/16) q6,q2; cp(-pi/8) q6,q3; cp(-pi/4) q6,q4; cp(-pi/2) q6,q5; h q6; cp(-pi/128) q7,q0; cp(-pi/64) q7,q1; cp(-pi/32) q7,q2; cp(-pi/16) q7,q3; cp(-pi/8) q7,q4; cp(-pi/4) q7,q5; cp(-pi/2) q7,q6; h q7; cp(-pi/256) q8,q0; cp(-pi/128) q8,q1; cp(-pi/64) q8,q2; cp(-pi/32) q8,q3; cp(-pi/16) q8,q4; cp(-pi/8) q8,q5; cp(-pi/4) q8,q6; cp(-pi/2) q8,q7; h q8; cp(-pi/512) q9,q0; cp(-pi/256) q9,q1; cp(-pi/128) q9,q2; cp(-pi/64) q9,q3; cp(-pi/32) q9,q4; cp(-pi/16) q9,q5; cp(-pi/8) q9,q6; cp(-pi/4) q9,q7; cp(-pi/2) q9,q8; h q9; cp(-pi/1024) q10,q0; cp(-pi/512) q10,q1; cp(-pi/256) q10,q2; cp(-pi/128) q10,q3; cp(-pi/64) q10,q4; cp(-pi/32) q10,q5; cp(-pi/16) q10,q6; cp(-pi/8) q10,q7; cp(-pi/4) q10,q8; cp(-pi/2) q10,q9; h q10; cp(-pi/2048) q11,q0; cp(-pi/1024) q11,q1; cp(-pi/512) q11,q2; cp(-pi/256) q11,q3; cp(-pi/128) q11,q4; cp(-pi/64) q11,q5; cp(-pi/32) q11,q6; cp(-pi/16) q11,q7; cp(-pi/8) q11,q8; cp(-pi/4) q11,q9; cp(-pi/2) q11,q10; h q11; cp(-pi/4096) q12,q0; cp(-pi/2048) q12,q1; cp(-pi/1024) q12,q2; cp(-pi/512) q12,q3; cp(-pi/256) q12,q4; cp(-pi/128) q12,q5; cp(-pi/64) q12,q6; cp(-pi/32) q12,q7; cp(-pi/16) q12,q8; cp(-pi/8) q12,q9; cp(-pi/4) q12,q10; cp(-pi/2) q12,q11; h q12; cp(-pi/8192) q13,q0; cp(-pi/4096) q13,q1; cp(-pi/2048) q13,q2; cp(-pi/1024) q13,q3; cp(-pi/512) q13,q4; cp(-pi/256) q13,q5; cp(-pi/128) q13,q6; cp(-pi/64) q13,q7; cp(-pi/32) q13,q8; cp(-pi/16) q13,q9; cp(-pi/8) q13,q10; cp(-pi/4) q13,q11; cp(-pi/2) q13,q12; h q13; cp(-pi/16384) q14,q0; cp(-pi/8192) q14,q1; cp(-pi/4096) q14,q2; cp(-pi/2048) q14,q3; cp(-pi/1024) q14,q4; cp(-pi/512) q14,q5; cp(-pi/256) q14,q6; cp(-pi/128) q14,q7; cp(-pi/64) q14,q8; cp(-pi/32) q14,q9; cp(-pi/16) q14,q10; cp(-pi/8) q14,q11; cp(-pi/4) q14,q12; cp(-pi/2) q14,q13; h q14; }
gate gate_QPE q0,q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15 { h q0; h q1; h q2; h q3; h q4; h q5; h q6; h q7; h q8; h q9; h q10; h q11; h q12; h q13; h q14; ccircuit_798 q0,q15; ccircuit_807 q1,q15; ccircuit_816 q2,q15; ccircuit_825 q3,q15; ccircuit_834 q4,q15; ccircuit_843 q5,q15; ccircuit_852 q6,q15; ccircuit_861 q7,q15; ccircuit_870 q8,q15; ccircuit_879 q9,q15; ccircuit_888 q10,q15; ccircuit_897 q11,q15; ccircuit_906 q12,q15; ccircuit_915 q13,q15; ccircuit_924 q14,q15; gate_IQFT_dg q14,q13,q12,q11,q10,q9,q8,q7,q6,q5,q4,q3,q2,q1,q0; }
qreg eval[15];
qreg q[1];
creg meas[16];
ry(0.9272952180016122) q[0];
gate_QPE eval[0],eval[1],eval[2],eval[3],eval[4],eval[5],eval[6],eval[7],eval[8],eval[9],eval[10],eval[11],eval[12],eval[13],eval[14],q[0];
barrier eval[0],eval[1],eval[2],eval[3],eval[4],eval[5],eval[6],eval[7],eval[8],eval[9],eval[10],eval[11],eval[12],eval[13],eval[14],q[0];
measure eval[0] -> meas[0];
measure eval[1] -> meas[1];
measure eval[2] -> meas[2];
measure eval[3] -> meas[3];
measure eval[4] -> meas[4];
measure eval[5] -> meas[5];
measure eval[6] -> meas[6];
measure eval[7] -> meas[7];
measure eval[8] -> meas[8];
measure eval[9] -> meas[9];
measure eval[10] -> meas[10];
measure eval[11] -> meas[11];
measure eval[12] -> meas[12];
measure eval[13] -> meas[13];
measure eval[14] -> meas[14];
measure q[0] -> meas[15];
