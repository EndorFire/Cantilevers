
import re 
import os 
def main(FOLDERNAME, CHOICES):
    if CHOICES[0]: 
        Pulses(FOLDERNAME)
    if CHOICES[1]: 
        Voltammetry(FOLDERNAME)

def Pulses(FOLDERNAME): 
    PULSEDELTAV = .25
    fileNums = checkFiles(FOLDERNAME, "Pulses")
    mergeBiologicPulse(fileNums)
    zeroBiologicPulse(fileNums, PULSEDELTAV)
    zeroPXIPulse(fileNums, PULSEDELTAV, FOLDERNAME)
    combinePulse(fileNums)
    for num in fileNums:
        os.remove(f"CorrectedPXIPulse#{num}.txt")
        os.remove(f"CorrectedBiologicPulse#{num}.txt")
        os.remove(f"Temp#{num}.txt")

def Voltammetry(FOLDERNAME): 
    PointCheck = 5

    fileNums = checkFiles(FOLDERNAME, "Voltammetry")
    mergeBiologicVoltammetry(fileNums)  
    bioPeak = zeroBiologicVoltammetry(fileNums, PointCheck)
    zeroPXIVoltammetry(fileNums, PointCheck, bioPeak, FOLDERNAME)
    combineVoltammetry(fileNums)
    for num in fileNums:
        os.remove(f"CorrectedPXICyclic#{num}.txt")
        os.remove(f"CorrectedBiologicVoltammetry#{num}.txt")
        os.remove(f"Temp#{num}.txt")

def checkFiles(FOLDERNAME, FILENAME):
    listBiologic = set()
    listPXI = set()

    for name in os.listdir(FOLDERNAME + f"\\Biologic\\{FILENAME}"): 
        if re.match(r".*\.mpt$", name):
            listBiologic.add(re.search(r"#(\d+)", name).group(1))
            
    PXIFiles = os.listdir(FOLDERNAME + f"\\PXI\\{FILENAME}")
    for name in PXIFiles:
        listPXI.add(re.search(r"#(\d+)", name).group(1))
    
    return sorted(list(listBiologic & listPXI))

def mergeBiologicPulse(fileNums):
    for num in fileNums: 
        bioFiles = []
        for name in sorted(os.listdir(FOLDERNAME + f"\\Biologic\\Pulses")): 
            if re.match(r".*#" + re.escape(num) + r"_.*\.mpt$", name):
                bioFiles.append(name)
        with open(f"Temp#{num}.txt", 'w') as f: 
            f.write("Time\tcontrol/V\tEwe/V\t<I>/mA\n")
            for file in bioFiles:
                with open(FOLDERNAME + f"\\Biologic\\Pulses\\" + file, 'r') as q: 
                    q.readline()
                    headers = int(q.readline().split(":")[1].strip())
                    for x in range(headers-1): 
                        q.readline()
                    
                    line = q.readline()
                    while line != "":
                        f.write("\t".join(line.split("\t")[7:11]) + "\n")
                        line = q.readline()

def mergeBiologicVoltammetry(fileNums):
    for num in fileNums: 
        bioFiles = []
        for name in sorted(os.listdir(FOLDERNAME + f"\\Biologic\\Voltammetry")): 
            if re.match(r".*#" + re.escape(num) + r"_.*\.mpt$", name):
                bioFiles.append(name)
        with open(f"Temp#{num}.txt", 'w') as f: 
            f.write("Time\tcontrol/V\tEwe/V\t<I>/mA\n")
            for file in bioFiles:
                with open(FOLDERNAME + f"\\Biologic\\Voltammetry\\" + file, 'r') as q: 
                    q.readline()
                    headers = int(q.readline().split(":")[1].strip())
                    for x in range(headers-1): 
                        q.readline()

                    if re.search(r"_CA_", file):
                        line = q.readline()
                        while line != "":
                            f.write("\t".join(line.split("\t")[7:11]) + "\n")
                            line = q.readline()
                    elif re.search(r"_CV_", file):
                        line = q.readline()
                        while line != "":
                            f.write("\t".join(line.split("\t")[5:9]) + "\n")
                            line = q.readline()

def zeroBiologicPulse(fileNums, PULSEDELTAV):
    for num in fileNums: 
        with open(f"Temp#{num}.txt", 'r') as f:
            f.readline()
            prev = f.readline().split("\t")
            line = f.readline().split("\t")
            while abs(float(prev[2])-float(line[2])) < PULSEDELTAV:
                prev = line
                line = f.readline().split("\t")
            zero = float(line[0])
        with open(f"Temp#{num}.txt", 'r') as f:
            with open(f"CorrectedBiologicPulse#{num}.txt", 'w') as q:
                q.write("Time\tcontrol/V\tEwe/V\t<I>/mA\n")
                f.readline()
                line = f.readline()
                while line != "": 
                    split = line.split("\t")
                    split[0] = str(float(split[0])-zero)
                    q.write("\t".join(split))
                    line = f.readline()

def zeroPXIPulse(fileNums, PULSEDELTAV, FOLDERNAME):
    for num in fileNums:
        with open(FOLDERNAME + f"\\PXI\\Pulses\\Pulse#{num}", 'r') as f: 
            for x in range(22):
                f.readline()
            prev = f.readline().split("\t")
            line = f.readline().split("\t")
            while abs(float(prev[5])-float(line[5])) < PULSEDELTAV:
                prev = line
                line = f.readline().split("\t")
            zero = float(line[0])
        with open(FOLDERNAME + f"\\PXI\\Pulses\\Pulse#{num}", 'r') as f:
            for x in range(21):
                f.readline() 
            with open(f"CorrectedPXIPulse#{num}.txt", 'w') as q:
                q.write(f.readline())
                line = f.readline()
                while line != "": 
                    split = line.split("\t")
                    split[0] = f"{float(split[0])-zero:.9f}"
                    q.write("\t".join(split))
                    line = f.readline()

def combinePulse(fileNums):
    for num in fileNums: 
        with open(f"CorrectedPXIPulse#{num}.txt", 'r') as f:
            with open(f"CorrectedBiologicPulse#{num}.txt", 'r') as q: 
                with open(f"CorrectedPulse#{num}.txt" , 'w') as p:
                    PXILine = f.readline().strip()
                    BiologicLine = q.readline().strip()
                    while (PXILine != "" or BiologicLine != ""):
                        p.write(PXILine + "\t" + BiologicLine + "\n")
                        PXILine = f.readline().strip()
                        BiologicLine = q.readline().strip()


def zeroBiologicVoltammetry(fileNums, PointCheck): 
    for num in fileNums: 
        with open(f"Temp#{num}.txt", 'r') as f:
            f.readline()

            points = [[] for x in range(PointCheck)] #Could lead to errors, will advise
            for x in range(PointCheck):
                points[x] = f.readline().split("\t")

            decreasing = float(points[PointCheck-1][2]) < float(points[0][2])
            smallvariation = abs(float(points[PointCheck-1][2]) < float(points[0][2])) <= .02

            while((not decreasing and not smallvariation) or smallvariation):  #Works for negative sweeps only, need to find better way
                for x in range(PointCheck-1):
                    points[x] = points[x+1]
                points[PointCheck-1] = f.readline().split("\t")
                decreasing = float(points[PointCheck-1][2]) < float(points[0][2])
                smallvariation = abs(float(points[PointCheck-1][2]) < float(points[0][2])) <= .02
            peak = float(points[int(PointCheck/2)][0])

        with open(f"Temp#{num}.txt", 'rb') as f:
            with open(f"CorrectedBiologicVoltammetry#{num}.txt", "wb") as destination:
                destination.write(f.read())

        return peak

def zeroPXIVoltammetry(fileNums, PointCheck, bioPeak,  FOLDERNAME): 
    for num in fileNums:
        with open(FOLDERNAME + f"\\PXI\\Voltammetry\\Cyclic#{num}", 'r') as f: 
            for x in range(25):
                f.readline()
            points = [[] for x in range(PointCheck)] #Could lead to errors, will advise
            for x in range(PointCheck):
                points[x] = f.readline().split("\t")

            while float(points[PointCheck-1][5]) < float(points[0][5]):
                for x in range(PointCheck):
                    points[x] = points[x+1]
                points[PointCheck-1] = f.readline().split("\t")
            peak = float(points[int(PointCheck/2)][0])

        with open(FOLDERNAME + f"\\PXI\\Voltammetry\\Cyclic#{num}", 'r') as f:
            peakdiff = peak-bioPeak
            with open(f"CorrectedPXICyclic#{num}.txt", 'w') as q:
                for x in range(25):
                    q.write(f.readline())
                line = f.readline()
                while line != "": 
                    split = line.split("\t")
                    split[0] = f"{float(split[0])-peakdiff:.9f}"
                    q.write("\t".join(split))
                    line = f.readline()

def combineVoltammetry(fileNums):
    for num in fileNums: 
        with open(f"CorrectedPXICyclic#{num}.txt", 'r') as f:
            for x in range(24): 
                f.readline()
            with open(f"CorrectedBiologicVoltammetry#{num}.txt", 'r') as q: 
                with open(f"CorrectedVoltammetry#{num}.txt" , 'w') as p:
                    PXILine = f.readline().strip()
                    BiologicLine = q.readline().strip()
                    while (PXILine != "" or BiologicLine != ""):
                        p.write(PXILine + "\t" + BiologicLine + "\n")
                        PXILine = f.readline().strip()
                        BiologicLine = q.readline().strip()

if __name__ == "__main__":
    FOLDERNAME = input("Folder Name (must be in current directory): ")
    PulsesChoice = input("Pulses? (y/n): ")
    VoltammetryChoice = input("Voltammetry? (y/n): ")
    CHOICES = [False, False]
    if(PulsesChoice.lower() in ("y", "yes")):
        CHOICES[0] = True
    if(VoltammetryChoice.lower() in ("y", "yes")):
        CHOICES[1] = True

    main(FOLDERNAME, CHOICES)
