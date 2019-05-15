# IIPSRV with Kakadu builder

This container will produce RPMs of IIPSRV with Kakadu support and Kakadu itself.

Because Kakadu is a licensed product, you will have to create a *kakadu* directory containing the unzipped software.

```
[carroarmato0@neon-flower:~/IIPSRV] master(+9/-2)* ± tree -L 3
.
├── Dockerfile
├── kakadu
│   └── v7_5-01574L
│       ├── apps
│       ├── bin
│       ├── Compiling_Instructions.txt
│       ├── coresys
│       ├── documentation
│       ├── language
│       ├── lib
│       ├── LICENSE.TXT
│       ├── mail_to
│       ├── make
│       ├── managed
│       └── Updates.txt
└── README.md
```

```
docker build ./
...
Removing intermediate container 3a239f320073
 ---> d189a799c72c
Successfully built d189a799c72c

docker run -it -v ${PWD}:/root/result d189a799c72c

[root@0ac37e01e7ae /]# cp /root/rpmbuild/RPMS/*/*.rpm /root/result; cp /kakadu-7.5.01574_1-1.x86_64.rpm /root/result
```