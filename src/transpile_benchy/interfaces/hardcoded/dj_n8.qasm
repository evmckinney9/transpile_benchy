OPENQASM 2.0;
include "qelib1.inc";
qreg q[8];
creg c[7];
u(pi/2,0,pi) q[0];
u(pi,0,pi) q[0];
u(pi/2,0,pi) q[1];
u(pi,0,pi) q[1];
u(pi/2,0,pi) q[2];
u(pi/2,0,pi) q[3];
u(pi,0,pi) q[3];
u(pi/2,0,pi) q[4];
u(pi/2,0,pi) q[5];
u(pi,0,pi) q[5];
u(pi/2,0,pi) q[6];
u(pi,0,pi) q[6];
u(pi,0,pi) q[7];
u(pi/2,0,pi) q[7];
cx q[0],q[7];
u(pi,0,pi) q[0];
u(pi/2,0,pi) q[0];
cx q[1],q[7];
u(pi,0,pi) q[1];
u(pi/2,0,pi) q[1];
cx q[2],q[7];
u(pi/2,0,pi) q[2];
cx q[3],q[7];
u(pi,0,pi) q[3];
u(pi/2,0,pi) q[3];
cx q[4],q[7];
u(pi/2,0,pi) q[4];
cx q[5],q[7];
u(pi,0,pi) q[5];
u(pi/2,0,pi) q[5];
cx q[6],q[7];
u(pi,0,pi) q[6];
u(pi/2,0,pi) q[6];
barrier q[0],q[1],q[2],q[3],q[4],q[5],q[6],q[7];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
measure q[4] -> c[4];
measure q[5] -> c[5];
measure q[6] -> c[6];
