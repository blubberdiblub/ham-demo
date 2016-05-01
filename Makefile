VEHICLE_NUMBERS := $(shell seq -w 0 15)
VEHICLES := $(patsubst %,generated/vehicle%.png,$(VEHICLE_NUMBERS))

.PHONY: all
all: animation frames atlas background vehicles

.PHONY: animation
animation: generated/animation.png

.PHONY: frames
frames: generated/frame000.png

.PHONY: atlas
atlas: generated/atlas.png

.PHONY: background
background: generated/background.png

.PHONY: vehicles
vehicles: $(VEHICLES)

.PHONY: clean
clean:
	rm -f -- generated/*

generated/animation.png: generated/frame000.png
	apngasm $@ $<

generated/frame000.png: ham-demo.py generated/background.png $(VEHICLES) resources/palette.txt
	python3 $<

generated/atlas.png: atlas.py generated/background.png $(VEHICLES)
	python3 $<

generated/background.png: background.ini background.pov
	povray $<

$(VEHICLES): vehicle.ini vehicle.pov resources/Pattern2D_01.jpg
	povray $<
