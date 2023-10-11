OPENQASM 2.0;
include "qelib1.inc";
qreg q[8];
creg meas[8];
u(pi/2,0,pi) q[7];
cx q[7],q[6];
cx q[6],q[5];
cx q[5],q[4];
cx q[4],q[3];
cx q[3],q[2];
cx q[2],q[1];
cx q[1],q[0];
u(pi/2,0,pi) q[7];
u(0,0,pi/4) q[7];
cx q[7],q[6];
u(0,0,-pi/4) q[6];
cx q[7],q[6];
u(0,0,pi/4) q[6];
u(pi/2,0,pi) q[6];
u(0,0,pi/4) q[6];
u(0,0,pi/8) q[7];
cx q[7],q[5];
u(0,0,-pi/8) q[5];
cx q[7],q[5];
u(0,0,pi/8) q[5];
cx q[6],q[5];
u(0,0,-pi/4) q[5];
cx q[6],q[5];
u(0,0,pi/4) q[5];
u(pi/2,0,pi) q[5];
u(0,0,pi/4) q[5];
u(0,0,pi/8) q[6];
u(0,0,pi/16) q[7];
cx q[7],q[4];
u(0,0,-pi/16) q[4];
cx q[7],q[4];
u(0,0,pi/16) q[4];
cx q[6],q[4];
u(0,0,-pi/8) q[4];
cx q[6],q[4];
u(0,0,pi/8) q[4];
cx q[5],q[4];
u(0,0,-pi/4) q[4];
cx q[5],q[4];
u(0,0,pi/4) q[4];
u(pi/2,0,pi) q[4];
u(0,0,pi/4) q[4];
u(0,0,pi/8) q[5];
u(0,0,pi/16) q[6];
u(0,0,pi/32) q[7];
cx q[7],q[3];
u(0,0,-pi/32) q[3];
cx q[7],q[3];
u(0,0,pi/32) q[3];
cx q[6],q[3];
u(0,0,-pi/16) q[3];
cx q[6],q[3];
u(0,0,pi/16) q[3];
cx q[5],q[3];
u(0,0,-pi/8) q[3];
cx q[5],q[3];
u(0,0,pi/8) q[3];
cx q[4],q[3];
u(0,0,-pi/4) q[3];
cx q[4],q[3];
u(0,0,pi/4) q[3];
u(pi/2,0,pi) q[3];
u(0,0,pi/4) q[3];
u(0,0,pi/8) q[4];
u(0,0,pi/16) q[5];
u(0,0,pi/32) q[6];
u(0,0,pi/64) q[7];
cx q[7],q[2];
u(0,0,-pi/64) q[2];
cx q[7],q[2];
u(0,0,pi/64) q[2];
cx q[6],q[2];
u(0,0,-pi/32) q[2];
cx q[6],q[2];
u(0,0,pi/32) q[2];
cx q[5],q[2];
u(0,0,-pi/16) q[2];
cx q[5],q[2];
u(0,0,pi/16) q[2];
cx q[4],q[2];
u(0,0,-pi/8) q[2];
cx q[4],q[2];
u(0,0,pi/8) q[2];
cx q[3],q[2];
u(0,0,-pi/4) q[2];
cx q[3],q[2];
u(0,0,pi/4) q[2];
u(pi/2,0,pi) q[2];
u(0,0,pi/4) q[2];
u(0,0,pi/8) q[3];
u(0,0,pi/16) q[4];
u(0,0,pi/32) q[5];
u(0,0,pi/64) q[6];
u(0,0,pi/128) q[7];
cx q[7],q[1];
u(0,0,-pi/128) q[1];
cx q[7],q[1];
u(0,0,pi/128) q[1];
cx q[6],q[1];
u(0,0,-pi/64) q[1];
cx q[6],q[1];
u(0,0,pi/64) q[1];
cx q[5],q[1];
u(0,0,-pi/32) q[1];
cx q[5],q[1];
u(0,0,pi/32) q[1];
cx q[4],q[1];
u(0,0,-pi/16) q[1];
cx q[4],q[1];
u(0,0,pi/16) q[1];
cx q[3],q[1];
u(0,0,-pi/8) q[1];
cx q[3],q[1];
u(0,0,pi/8) q[1];
cx q[2],q[1];
u(0,0,-pi/4) q[1];
cx q[2],q[1];
u(0,0,pi/4) q[1];
u(pi/2,0,pi) q[1];
u(0,0,pi/4) q[1];
u(0,0,pi/8) q[2];
u(0,0,pi/16) q[3];
u(0,0,pi/32) q[4];
u(0,0,pi/64) q[5];
u(0,0,pi/128) q[6];
u(0,0,pi/256) q[7];
cx q[7],q[0];
u(0,0,-pi/256) q[0];
cx q[7],q[0];
u(0,0,pi/256) q[0];
cx q[6],q[0];
u(0,0,-pi/128) q[0];
cx q[6],q[0];
u(0,0,pi/128) q[0];
cx q[5],q[0];
u(0,0,-pi/64) q[0];
cx q[5],q[0];
u(0,0,pi/64) q[0];
cx q[4],q[0];
u(0,0,-pi/32) q[0];
cx q[4],q[0];
u(0,0,pi/32) q[0];
cx q[3],q[0];
u(0,0,-pi/16) q[0];
cx q[3],q[0];
u(0,0,pi/16) q[0];
cx q[2],q[0];
u(0,0,-pi/8) q[0];
cx q[2],q[0];
u(0,0,pi/8) q[0];
cx q[1],q[0];
u(0,0,-pi/4) q[0];
cx q[1],q[0];
u(0,0,pi/4) q[0];
u(pi/2,0,pi) q[0];
cx q[0],q[7];
cx q[1],q[6];
cx q[2],q[5];
cx q[3],q[4];
cx q[4],q[3];
cx q[3],q[4];
cx q[5],q[2];
cx q[2],q[5];
cx q[6],q[1];
cx q[1],q[6];
cx q[7],q[0];
cx q[0],q[7];
barrier q[0],q[1],q[2],q[3],q[4],q[5],q[6],q[7];
measure q[0] -> meas[0];
measure q[1] -> meas[1];
measure q[2] -> meas[2];
measure q[3] -> meas[3];
measure q[4] -> meas[4];
measure q[5] -> meas[5];
measure q[6] -> meas[6];
measure q[7] -> meas[7];
