import gzip


for input_filename in ['efo.json', 'hancestro.owl', 'ms.owl', 'pride_cv_updated.obo', 'pride_cv.obo', 'psi-ms.obo', 'unimod.csv']:
    output_filename = input_filename + ".gz"

    with open(input_filename, 'rb') as f_in:
        with gzip.open(output_filename, 'wb') as f_out:
            f_out.writelines(f_in)

    print(f'Compressed {input_filename} to {output_filename}')