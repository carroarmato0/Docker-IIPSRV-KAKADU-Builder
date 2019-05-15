# IIPSRV with Kakadu builder

This container will produce an RPM of IIPSRV with Kakadu support.

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