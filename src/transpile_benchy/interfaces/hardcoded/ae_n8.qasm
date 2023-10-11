OPENQASM 2.0;
include "qelib1.inc";
qreg eval[7];
qreg q[1];
creg meas[8];
u(pi/2,0,pi) eval[0];
u(0,0,0) eval[0];
u(pi/2,0,pi) eval[1];
u(0,0,0) eval[1];
u(pi/2,0,pi) eval[2];
u(0,0,0) eval[2];
u(pi/2,0,pi) eval[3];
u(0,0,0) eval[3];
u(pi/2,0,pi) eval[4];
u(0,0,0) eval[4];
u(pi/2,0,pi) eval[5];
u(0,0,0) eval[5];
u(pi/2,0,pi) eval[6];
u(0,0,0) eval[6];
u(0.9272952180016122,0,0) q[0];
u(0,0,0) q[0];
cx eval[0],q[0];
u(-0.9272952180016122,0,0) q[0];
cx eval[0],q[0];
u(0.9272952180016122,0,0) q[0];
u(0,0,0) q[0];
u(0,0,-pi/128) eval[0];
cx eval[1],q[0];
u(-1.8545904360032244,0,0) q[0];
cx eval[1],q[0];
u(1.8545904360032244,0,0) q[0];
u(0,0,0) q[0];
u(0,0,-pi/64) eval[1];
cx eval[2],q[0];
u(-3.7091808720064487,0,0) q[0];
cx eval[2],q[0];
u(3.7091808720064487,0,0) q[0];
u(0,0,0) q[0];
u(0,0,-pi/32) eval[2];
cx eval[3],q[0];
u(-7.4183617440128975,0,0) q[0];
cx eval[3],q[0];
u(7.4183617440128975,0,0) q[0];
u(0,0,0) q[0];
u(0,0,-pi/16) eval[3];
cx eval[4],q[0];
u(-14.836723488025795,0,0) q[0];
cx eval[4],q[0];
u(14.836723488025795,0,0) q[0];
u(0,0,0) q[0];
u(0,0,-pi/8) eval[4];
cx eval[5],q[0];
u(-29.67344697605159,0,0) q[0];
cx eval[5],q[0];
u(29.67344697605159,0,0) q[0];
u(0,0,0) q[0];
u(0,0,-pi/4) eval[5];
cx eval[6],q[0];
u(-59.34689395210318,0,0) q[0];
cx eval[6],q[0];
u(59.34689395210318,0,0) q[0];
u(pi/2,0,pi) eval[6];
cx eval[5],eval[6];
u(0,0,pi/4) eval[6];
cx eval[5],eval[6];
u(pi/2,0,pi) eval[5];
u(0,0,-pi/4) eval[6];
cx eval[4],eval[6];
u(0,0,pi/8) eval[6];
cx eval[4],eval[6];
u(0,0,-pi/4) eval[4];
cx eval[4],eval[5];
u(0,0,pi/4) eval[5];
cx eval[4],eval[5];
u(pi/2,0,pi) eval[4];
u(0,0,-pi/4) eval[5];
u(0,0,-pi/8) eval[6];
cx eval[3],eval[6];
u(0,0,pi/16) eval[6];
cx eval[3],eval[6];
u(0,0,-pi/8) eval[3];
cx eval[3],eval[5];
u(0,0,pi/8) eval[5];
cx eval[3],eval[5];
u(0,0,-pi/4) eval[3];
cx eval[3],eval[4];
u(0,0,pi/4) eval[4];
cx eval[3],eval[4];
u(pi/2,0,pi) eval[3];
u(0,0,-pi/4) eval[4];
u(0,0,-pi/8) eval[5];
u(0,0,-pi/16) eval[6];
cx eval[2],eval[6];
u(0,0,pi/32) eval[6];
cx eval[2],eval[6];
u(0,0,-pi/16) eval[2];
cx eval[2],eval[5];
u(0,0,pi/16) eval[5];
cx eval[2],eval[5];
u(0,0,-pi/8) eval[2];
cx eval[2],eval[4];
u(0,0,pi/8) eval[4];
cx eval[2],eval[4];
u(0,0,-pi/4) eval[2];
cx eval[2],eval[3];
u(0,0,pi/4) eval[3];
cx eval[2],eval[3];
u(pi/2,0,pi) eval[2];
u(0,0,-pi/4) eval[3];
u(0,0,-pi/8) eval[4];
u(0,0,-pi/16) eval[5];
u(0,0,-pi/32) eval[6];
cx eval[1],eval[6];
u(0,0,pi/64) eval[6];
cx eval[1],eval[6];
u(0,0,-pi/32) eval[1];
cx eval[1],eval[5];
u(0,0,pi/32) eval[5];
cx eval[1],eval[5];
u(0,0,-pi/16) eval[1];
cx eval[1],eval[4];
u(0,0,pi/16) eval[4];
cx eval[1],eval[4];
u(0,0,-pi/8) eval[1];
cx eval[1],eval[3];
u(0,0,pi/8) eval[3];
cx eval[1],eval[3];
u(0,0,-pi/4) eval[1];
cx eval[1],eval[2];
u(0,0,pi/4) eval[2];
cx eval[1],eval[2];
u(pi/2,0,pi) eval[1];
u(0,0,-pi/4) eval[2];
u(0,0,-pi/8) eval[3];
u(0,0,-pi/16) eval[4];
u(0,0,-pi/32) eval[5];
u(0,0,-pi/64) eval[6];
cx eval[0],eval[6];
u(0,0,pi/128) eval[6];
cx eval[0],eval[6];
u(0,0,-pi/64) eval[0];
cx eval[0],eval[5];
u(0,0,pi/64) eval[5];
cx eval[0],eval[5];
u(0,0,-pi/32) eval[0];
cx eval[0],eval[4];
u(0,0,pi/32) eval[4];
cx eval[0],eval[4];
u(0,0,-pi/16) eval[0];
cx eval[0],eval[3];
u(0,0,pi/16) eval[3];
cx eval[0],eval[3];
u(0,0,-pi/8) eval[0];
cx eval[0],eval[2];
u(0,0,pi/8) eval[2];
cx eval[0],eval[2];
u(0,0,-pi/4) eval[0];
cx eval[0],eval[1];
u(0,0,pi/4) eval[1];
cx eval[0],eval[1];
u(pi/2,0,pi) eval[0];
u(0,0,-pi/4) eval[1];
u(0,0,-pi/8) eval[2];
u(0,0,-pi/16) eval[3];
u(0,0,-pi/32) eval[4];
u(0,0,-pi/64) eval[5];
u(0,0,-pi/128) eval[6];
barrier eval[0],eval[1],eval[2],eval[3],eval[4],eval[5],eval[6],q[0];
measure eval[0] -> meas[0];
measure eval[1] -> meas[1];
measure eval[2] -> meas[2];
measure eval[3] -> meas[3];
measure eval[4] -> meas[4];
measure eval[5] -> meas[5];
measure eval[6] -> meas[6];
measure q[0] -> meas[7];
