CC=gcc
CFLAGS=-I.

SOURCE = track_features.c
ARCH = klt/convolve.c klt/error.c klt/pnmio.c klt/pyramid.c \
	klt/selectGoodFeatures.c klt/storeFeatures.c klt/trackFeatures.c \
	klt/klt.c klt/klt_util.c klt/writeFeatures.c
ARCH_NOINC = convolve.c error.c pnmio.c pyramid.c selectGoodFeatures.c \
	storeFeatures.c trackFeatures.c klt.c klt_util.c writeFeatures.c
LIB = -L/usr/local/lib -L/usr/lib

.SUFFIXES:  .c .o

all: lib $(SOURCE:.c=)

.c.o:
	$(CC) -c $(CFLAGS) $<

lib: $(ARCH:.c=.o)
	rm -f libklt.a
	ar ruv libklt.a $(ARCH_NOINC:.c=.o)
	rm -f *.o

track_features: libklt.a
	$(CC) -O3 $(CFLAGS) -o $@ $@.c -L./klt -lklt $(LIB) -lm
	mv track_features ../track_features

depend:
	makedepend klt/$(ARCH) $(EXAMPLES)

tracker: $(OBJ)
	$(CC) -o tracker -L. -lklt $^ $(CFLAGS)

clean:
	rm -f *.o *.a $(SOURCE:.c=) *.tar *.tar.gz libklt.a *.o
