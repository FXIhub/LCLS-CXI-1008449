ds = psana.MPIDataSource(f'exp={EXP_NAME}:run={27}:smd')
det = psana.Detector(DET_NAME)
timestamps, run_intens = get_run_intens(27)
med = np.median(run_intens)

loc = np.where(run_intens < 10*med)
timestamps, run_intens = timestamps[loc], run_intens[loc]

loc = np.where(run_intens > med/10)
timestamps, run_intens = timestamps[loc], run_intens[loc]

p16 = np.percentile(run_intens, 16)
p84 = np.percentile(run_intens, 84)
wid = p84 - p16

for i, event in enumerate(ds.events()):
    print(i)
    calib = det.calib(event)

    intens = calib.sum()

    if intens>med+wid:
        assem_run_mean = det.image(evt, calib)

        break
plt.imshow(assem_run_mean)