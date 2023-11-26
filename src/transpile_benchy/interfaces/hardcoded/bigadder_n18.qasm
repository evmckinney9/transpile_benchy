OPENQASM 2.0;
include "qelib1.inc";
gate majority q0,q1,q2 { cx q2,q1; cx q2,q0; ccx q0,q1,q2; }
gate unmaj q0,q1,q2 { ccx q0,q1,q2; cx q2,q0; cx q0,q1; }
gate add4 q0,q1,q2,q3,q4,q5,q6,q7,q8,q9 { majority q8,q4,q0; majority q0,q5,q1; majority q1,q6,q2; majority q2,q7,q3; cx q3,q9; unmaj q2,q7,q3; unmaj q1,q6,q2; unmaj q0,q5,q1; unmaj q8,q4,q0; }
qreg carry[2];
qreg a[8];
qreg b[8];
creg ans[8];
creg carryout[1];
x a[0];
x b[0];
x b[1];
x b[2];
x b[3];
x b[4];
x b[5];
x b[6];
x b[7];
x b[6];
add4 a[0],a[1],a[2],a[3],b[0],b[1],b[2],b[3],carry[0],carry[1];
add4 a[4],a[5],a[6],a[7],b[4],b[5],b[6],b[7],carry[1],carry[0];
measure b[0] -> ans[0];
measure b[1] -> ans[1];
measure b[2] -> ans[2];
measure b[3] -> ans[3];
measure b[4] -> ans[4];
measure b[5] -> ans[5];
measure b[6] -> ans[6];
measure b[7] -> ans[7];
measure carry[0] -> carryout[0];
