# XPO ( Xenopus Phenotype Ontology ) - Runbook (0.1)

This runbooks provides the steps to prepare the templates and the scripts involved in the XPO generation. 
The github repo [XPO](https://github.com/obophenotype/xenopus-phenotype-ontology/). 



## In a Nutshell

Look at the Makefile in /src/ontology and the xpo.Makefile. Snippets from each are given below
to help orientate and provide insight into what is going on under the hood.

Essentially through the skillful use of **make** targets we build a number of intermediate files and
use those to construct the xpo.owl and xpo.obo. 
ROBOT plays an important part together DOS-DP and SPARQL.

```
ROBOT=                      robot --catalog $(CATALOG)
DOSDPT=                      dosdp-tools

```


If you happen to need a refresher for **make** then read this [make tutorial](https://www.sas.upenn.edu/~jesusfv/Chapter_HPC_6_Make.pdf)
.

```

Automatic variables are reserved expressions for targets and dependencies to be used within
rules. (For all such variables: see https://www.gnu.org/software/make/manual/html_
node/Automatic-Variables.html.) The most common ones are:
• $@ is the target of the current rule.
• $< is the first dependency of the current rule.
• $ˆ is all of the dependencies of the current rule.


```

#####  explore these ...


```

Describe the steps that are taken to run this python script:
/src/scripts has xpo_anatomy_pipeline.py
https://github.com/obophenotype/xenopus-phenotype-ontology/blob/master/src/scripts/xpo_anatomy_pipeline.py

see the /src/patterns/Makefile for: 

anatomy_pipeline: download_patterns $(XAO) $(ID_MAP) $(RESERVED_IRI) 
	echo "Using $(XAO_IRI), make sure this is correct!"
	python3 ../scripts/xpo_anatomy_pipeline.py  $(XAO) $(ID_MAP) $(RESERVED_IRI) dosdp-patterns $(SPARQLDIR) $(PIPELINE_DATA_PATH) $(PATTERN_CONFIG)


#########################################
### Generating all ROBOT templates ######
#########################################

TEMPLATES=$(patsubst %.tsv, templates/%.owl, $(notdir $(wildcard $(TEMPLATEDIR)/*.tsv)))

templates/%.owl: templates/%.tsv
	robot -vvv merge --catalog ../ontology/catalog-v001.xml --input $(SRC) template   --prefix 'rdfs: http://www.w3.org/2000/01/rdf-schema#'  --prefix "IAO: http://purl.obolibrary.org/obo/IAO_" --template $< --output $@ && \
	robot annotate --input $@ --ontology-iri $(OBOPURL)xpo/patterns/$@ -o $@




/src/metadata has the xenbase_phenotype_annotation.csv
https://github.com/obophenotype/xenopus-phenotype-ontology/blob/master/src/metadata/xenbase_phenotype_annotation.csv


```



## Getting Started



We need to understand the ecosystem for ODK and reading the developer notes is a good place to begin:
[ODK Developer info](https://github.com/INCATools/ontology-development-kit/blob/master/README-developers.md)


ODK makes use of [ROBOT](https://github.com/ontodev/robot) , ROBOT is a OBO Tool.
ODK also makes use of patterns as in [DOS-DP](https://github.com/INCATools/dead_simple_owl_design_patterns)


Do not miss taking a [fast track guide](https://docs.google.com/presentation/d/1nIybviEEJiRKHO2rkBMZsQ0QjtsHyU01_-9beZqD_Z4/edit#slide=id.g2690ff5cec_0_121)
Also see the [ODK intro](https://douroucouli.wordpress.com/2018/08/06/new-version-of-ontology-development-kit-now-with-docker-support/)
.


in the /src/ontology we find
xpo-odk.yaml gives us this, which shows that the artifacts are base, full and simple

```
id: xpo
title: "Xenopus Phenotype Ontology"
github_org: obophenotype
repo: xenopus-phenotype-ontology
report_fail_on: ERROR
use_dosdps: TRUE
dosdp_tools_options: "--obo-prefixes=true"
namespaces: 
  - http://purl.obolibrary.org/obo/XPO_
release_artefacts: 
  - base
  - full
  - simple
primary_release: full
export_formats:
  - owl
  - obo
  - json
import_group:
  products:
    - id: iao
    - id: go
    - id: ro
    - id: chebi
    - id: pato
    - id: bfo
    - id: xao
    - id: nbo
pattern_pipelines_group:
  products:
    - id: manual
      dosdp_tools_options: "--obo-prefixes=true"
    - id: anatomy
      dosdp_tools_options: "--obo-prefixes=true"
robot_java_args: '-Xmx8G'
allow_equivalents: none
```


#### The Makefile contains the paragraph # Initiating Step: Reason over source

This shows where the simple_seed.txt and xpo-edit.owl get used, as well as the patterns.owl and definitions.owl



```

URIBASE=                    http://purl.obolibrary.org/obo
ONT=                        xpo
ONTBASE=                    $(URIBASE)/$(ONT)
EDIT_FORMAT=                owl
SRC =                       $(ONT)-edit.$(EDIT_FORMAT)



SIMPLESEED=simple_seed.txt

OTHER_SRC = $(PATTERNDIR)/definitions.owl 


$(ONTOLOGYTERMS): $(SRC) $(OTHER_SRC)
	$(ROBOT) query --use-graphs true -f csv -i $< --query ../sparql/xpo_terms.sparql $@





SRCMERGED=merged-$(SRC)

$(SRCMERGED): $(SRC)
	$(ROBOT) remove --input $< --select imports --trim true \
		merge  $(patsubst %, -i %, $(OTHER_SRC)) -o $@





$(SIMPLESEED): $(SRCMERGED) $(ONTOLOGYTERMS)
	$(ROBOT) query --use-graphs false -f csv -i $< --query ../sparql/simple-seed.sparql $@.tmp &&\
	cat $@.tmp $(ONTOLOGYTERMS) | sort | uniq >  $@ &&\
	echo "http://www.geneontology.org/formats/oboInOwl#SubsetProperty" >> $@ &&\
	echo "http://www.geneontology.org/formats/oboInOwl#SynonymTypeProperty" >> $@





$(ONT)-simple.owl: $(SRC) $(OTHER_SRC) $(SIMPLESEED)
	$(ROBOT) merge --input $< $(patsubst %, -i %, $(OTHER_SRC)) \
		reason --reasoner ELK --equivalent-classes-allowed none --exclude-tautologies structural \
		relax \
		remove --axioms equivalent \
		relax \
		filter --term-file $(SIMPLESEED) --select "annotations ontology anonymous self" --trim true --signature true \
		reduce -r ELK \
		query --update ../sparql/inject-subset-declaration.ru \
		annotate --ontology-iri $(ONTBASE)/$@ --version-iri $(ONTBASE)/releases/$(TODAY)/$@ --output $@.tmp.owl && mv $@.tmp.owl $@




# Full: The full artefacts with imports merged, reasoned
$(ONT)-full.owl: $(SRC) $(OTHER_SRC)
	$(ROBOT) merge --input $< \
		reason --reasoner ELK --equivalent-classes-allowed none --exclude-tautologies structural \
		relax \
		reduce -r ELK \
		annotate --ontology-iri $(ONTBASE)/$@ --version-iri $(ONTBASE)/releases/$(TODAY)/$@ --output $@.tmp.owl && mv $@.tmp.owl $@






```


#### The Makefile contains the # Patterns (experimental) paragraph, which makes use of /patterns/definitions.owl

As we have seen the variable: OTHER_SRC = $(PATTERNDIR)/definitions.owl

Note that the variable: PATTERN_RELEASE_FILES=       $(PATTERNDIR)/definitions.owl $(PATTERNDIR)/pattern.owl


```

# prep the pattern.owl and the definitions.owl intermediate files
.PHONY: patterns
patterns: all_imports $(PATTERNDIR)/pattern.owl $(PATTERNDIR)/definitions.owl


# Generating the pattern.owl file
$(PATTERNDIR)/pattern.owl: pattern_schema_checks update_patterns
	@if [ $(PAT) = true ]; then $(DOSDPT) prototype --obo-prefixes --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi


# Generating the individual pattern modules and merging them into definitions.owl
$(PATTERNDIR)/definitions.owl: prepare_patterns update_patterns $(individual_patterns_default)   $(individual_patterns_manual) $(individual_patterns_anatomy)
	@if [ $(PAT) = true ]; then $(ROBOT) merge $(addprefix -i , $(individual_patterns_default))   $(addprefix -i , $(individual_patterns_manual)) $(addprefix -i , $(individual_patterns_anatomy)) annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl  --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions.owl -o definitions.ofn && mv definitions.ofn $@; fi



# Generating the seed file from all the TSVs. If Pattern generation is deactivated, we still extract a seed from definitions.owl
$(PATTERNDIR)/all_pattern_terms.txt: $(pattern_term_lists_default)   $(pattern_term_lists_manual) $(pattern_term_lists_anatomy) $(PATTERNDIR)/pattern_owl_seed.txt
	@if [ $(PAT) = true ]; then cat $^ | sort | uniq > $@; else $(ROBOT) query --use-graphs true -f csv -i ../patterns/definitions.owl --query ../sparql/terms.sparql $@; fi




```


#### The Makefile contains the Release Management paragraph and we find that the patterns folder is added and populated

```

# This should be executed by the release manager whenever time comes to make a release.
# It will ensure that all assets/files are fresh, and will copy to release folder
prepare_release: $(ASSETS) $(PATTERN_RELEASE_FILES)
	rsync -R $(ASSETS) $(RELEASEDIR) &&\
  mkdir -p $(RELEASEDIR)/patterns &&\
  cp $(PATTERN_RELEASE_FILES) $(RELEASEDIR)/patterns &&\
  echo "Release files are now in $(RELEASEDIR) - now you should commit, push and make a release on your git hosting site such as GitHub or GitLab"


```

#### The xpo.Makefile has the following targets

```

xpo_table.csv:
 which is based on ../sparql/xpo_metadata_table.sparql

xpo-xenbase.owl:
 which is based on simple_seed_xenbase.txt


xpo-xenbase.obo:
 which is based on xpo-xenbase.owl


```
xpo_table.csv can be found in this folder: xenopus-phenotype-ontology\src\ontology

In the examples that follow we make use of XPO_0102262 to provide comparison and trace it through the various phases of the pipeline.
xpo_table.csv contains the following fields:
```
term,label,definition,exact_synonym
http://purl.obolibrary.org/obo/XPO_0102262,abnormal morphology of neurocoel ,Any structural anomaly of the neurocoel.,abnormal shape of neurocoel

```

These are materialized into xpo-merged.obo as
```
[Term]
id: XPO:0102262
name: abnormal morphology of neurocoel 
def: "Any structural anomaly of the neurocoel." []
synonym: "abnormal shape of neurocoel" EXACT []
synonym: "abnormally shaped neurocoel" EXACT []
is_a: XPO:0100630 ! abnormal neurocoel
is_a: XPO:0101694 ! abnormal morphology of anatomical space

```

The xpo.obo ( full ) gives us
```
[Term]
id: XPO:0102262
name: abnormal neurocoel morphology
def: "Any unspecified morphological anomaly of the neurocoel, such as, for example, abnormal shape or colour." []
synonym: "abnormal morphology of neurocoel" EXACT []
is_a: XPO:0100630 ! abnormal neurocoel
is_a: XPO:0101694 ! abnormal anatomical space morphology

```


The simple_seed.txt has the following:

```
cls
http://purl.obolibrary.org/obo/BFO_0000050
http://purl.obolibrary.org/obo/BFO_0000051
http://purl.obolibrary.org/obo/BFO_0000066
http://purl.obolibrary.org/obo/IAO_0000115
http://purl.obolibrary.org/obo/RO_0000052
http://purl.obolibrary.org/obo/RO_0002295
http://purl.obolibrary.org/obo/RO_0002314
http://purl.obolibrary.org/obo/RO_0002503
http://purl.obolibrary.org/obo/RO_0002565
http://purl.obolibrary.org/obo/RO_0002573
http://purl.obolibrary.org/obo/XPO_00000000
http://purl.obolibrary.org/obo/XPO_0100002

...

http://purl.obolibrary.org/obo/XPO_0141316
http://purl.obolibrary.org/obo/XPO_0141317
http://purl.org/dc/elements/1.1/description
http://purl.org/dc/elements/1.1/title
http://purl.org/dc/terms/license
http://www.geneontology.org/formats/oboInOwl#hasExactSynonym
term
http://www.geneontology.org/formats/oboInOwl#SubsetProperty
http://www.geneontology.org/formats/oboInOwl#SynonymTypeProperty


```





#### The xpo-idranges.owl provides three range groups


```
        allocatedto: "ONTOLOGY-CREATOR"
        xsd:integer[>= 0 , <= 999999]

    
        allocatedto: "ADDITIONAL EDITOR"
        xsd:integer[>= 1000000 , <= 1999999]
    
        allocatedto: "TermGenie"
        xsd:integer[> 2000000 , <= 2999999]

```


#### The xpo-equivalents.owl contains this
```
    <!-- http://purl.obolibrary.org/obo/XPO_0102262 -->

    <owl:Class rdf:about="http://purl.obolibrary.org/obo/XPO_0102262">
        <owl:equivalentClass>
            <owl:Restriction>
                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/BFO_0000051"/>
                <owl:someValuesFrom>
                    <owl:Class>
                        <owl:intersectionOf rdf:parseType="Collection">
                            <rdf:Description rdf:about="http://purl.obolibrary.org/obo/PATO_0000051"/>
                            <owl:Restriction>
                                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0000052"/>
                                <owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/XAO_0000252"/>
                            </owl:Restriction>
                            <owl:Restriction>
                                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0002573"/>
                                <owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/PATO_0000460"/>
                            </owl:Restriction>
                        </owl:intersectionOf>
                    </owl:Class>
                </owl:someValuesFrom>
            </owl:Restriction>
        </owl:equivalentClass>
        <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/XPO_0100630"/>
        <rdfs:subClassOf rdf:resource="http://purl.obolibrary.org/obo/XPO_0101694"/>
        <rdfs:subClassOf>
            <owl:Restriction>
                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/BFO_0000051"/>
                <owl:someValuesFrom>
                    <owl:Class>
                        <owl:intersectionOf rdf:parseType="Collection">
                            <rdf:Description rdf:about="http://purl.obolibrary.org/obo/PATO_0000051"/>
                            <owl:Restriction>
                                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0000052"/>
                                <owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/XAO_0000252"/>
                            </owl:Restriction>
                            <owl:Restriction>
                                <owl:onProperty rdf:resource="http://purl.obolibrary.org/obo/RO_0002573"/>
                                <owl:someValuesFrom rdf:resource="http://purl.obolibrary.org/obo/PATO_0000460"/>
                            </owl:Restriction>
                        </owl:intersectionOf>
                    </owl:Class>
                </owl:someValuesFrom>
            </owl:Restriction>
        </rdfs:subClassOf>
    </owl:Class>
    



```



### Prerequisites

The expectation is that we want to understand how to take the existing XPO and add to it in one way or another.
We can clone the XPO and ODK from github and use that to explore the functionality. 

In order to better understand how this works from scratch.
Typically we seed a new ontology thus:
We make use of a linux o/s running docker and clone the ODK so that you get the seed-via-docker.sh script.

Prep the new ontology using the seed-via-docker.sh command as described in [ODK](https://github.com/INCATools/ontology-development-kit/blob/master/README.md)

```
./seed-via-docker.sh -d po -d ro -d pato -u jsmith -t "example configured homogeneous ontology" echo
```

The /target/echo folder then contains the initialized ontology that is ready for github. 
Expect to find the following folders within /src ...
```
metadata
ontology
patterns
scripts
sparql
```

The /src/ontology folder has the Makefile and the run.sh script that are used subsequently for the various tasks such as test , patterns etc.
There is a test.sh, build.sh, patterns.sh all of which take the action you expect from them. For example
the build.sh does this ...

```
#!/bin/sh
./run.sh make all
```


There is a xpo.Makefile for custom make targets.



Expect to find the following folders within /src/ontology ...
```
imports
reports
tmp
```







```
Give examples

/src/ontology has several  folders and the all important Makefile and run.sh

# See README-editors.md for more details.
docker run -v $PWD/../../:/work -w /work/src/ontology -e ROBOT_JAVA_ARGS='-Xmx8G' --rm -ti obolibrary/odkfull "$@"




/src/patterns has several folders and the all important Makefile and run.sh

# See README-editors.md for more details.
docker run -v $PWD/../../:/work -w /work/src/patterns --rm -ti obolibrary/odkfull "$@"


https://github.com/obophenotype/xenopus-phenotype-ontology/tree/master/src/patterns/data

anatomy
manual
todo



Describe the steps that are taken to run this python script:
https://github.com/obophenotype/xenopus-phenotype-ontology/blob/master/src/scripts/xpo_anatomy_pipeline.py



/src/metadata has the xenbase_phenotype_annotation.csv
https://github.com/obophenotype/xenopus-phenotype-ontology/blob/master/src/metadata/xenbase_phenotype_annotation.csv




 REMEMBER TO SET UP YOUR GITHUB REPO FOR TRAVIS
 Go to: https://travis-ci.org/obophenotype for details

```


#### TODO: Add a UML Activity diagram to show the workflow.






### The /patterns/pattern.owl gives us this:


```

# Class: <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalDevelopmentOfAnatomicalEntity.yaml> (abnormal development of 'anatomical entity')

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalDevelopmentOfAnatomicalEntity.yaml> "An abnormal development of the 'anatomical entity'."^^xsd:string)
AnnotationAssertion(<http://purl.org/dc/terms/title> <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalDevelopmentOfAnatomicalEntity.yaml> "abnormalDevelopmentOfAnatomicalEntity"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalDevelopmentOfAnatomicalEntity.yaml> "abnormal development of 'anatomical entity'"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalDevelopmentOfAnatomicalEntity.yaml> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(<http://purl.obolibrary.org/obo/PATO_0001236> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> ObjectIntersectionOf(<http://purl.obolibrary.org/obo/GO_0032502> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002295> <http://purl.obolibrary.org/obo/UBERON_0001062>))) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))

# Class: <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalMolecularFunction.yaml> (abnormal 'molecular function')

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalMolecularFunction.yaml> "Abnormal 'molecular function'."^^xsd:string)
AnnotationAssertion(<http://purl.org/dc/terms/title> <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalMolecularFunction.yaml> "abnormalMolecularFunction"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalMolecularFunction.yaml> "abnormal 'molecular function'"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/upheno/patterns-dev/abnormalMolecularFunction.yaml> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(<http://purl.obolibrary.org/obo/PATO_0001236> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> <http://purl.obolibrary.org/obo/GO_0003674>) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))


# Class: <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntity.yaml> (abnormally formed 'anatomical entity')

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntity.yaml> "An abnormally formed/malformed 'anatomical entity'."^^xsd:string)
AnnotationAssertion(<http://purl.org/dc/terms/title> <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntity.yaml> "malformedAnatomicalEntity"^^xsd:string)
AnnotationAssertion(<http://www.geneontology.org/formats/oboInOwl#hasExactSynonym> <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntity.yaml> "malformed 'anatomical entity'"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntity.yaml> "abnormally formed 'anatomical entity'"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntity.yaml> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(<http://purl.obolibrary.org/obo/PATO_0000646> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> <http://purl.obolibrary.org/obo/UBERON_0001062>) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))

# Class: <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntityByType.yaml> ('malformed' 'anatomical entity')

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntityByType.yaml> "A 'malformed' 'anatomical entity'."^^xsd:string)
AnnotationAssertion(<http://purl.org/dc/terms/title> <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntityByType.yaml> "malformedAnatomicalEntityByType"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntityByType.yaml> "'malformed' 'anatomical entity'"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/upheno/patterns-dev/malformedAnatomicalEntityByType.yaml> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(<http://purl.obolibrary.org/obo/PATO_0000646> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> <http://purl.obolibrary.org/obo/UBERON_0001062>) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))



# Class: <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyInLocationTEMP.yaml> (abnormal(ly) 'quality' of 'entity' in 'entity' (T))

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyInLocationTEMP.yaml> "Abnormal(ly) 'quality' of 'entity' in 'entity' (Temporary definition)."^^xsd:string)
AnnotationAssertion(<http://purl.org/dc/terms/title> <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyInLocationTEMP.yaml> "xpoAnatomyInLocationTEMP"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyInLocationTEMP.yaml> "abnormal(ly) 'quality' of 'entity' in 'entity' (T)"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyInLocationTEMP.yaml> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(owl:Thing ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> ObjectIntersectionOf(owl:Thing ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000050> owl:Thing))) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))

# Class: <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyTEMP.yaml> (abnormal(ly) 'quality' of 'entity' (T))

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyTEMP.yaml> "Abnormal(ly) 'quality' of 'entity' (Temporary definition)."^^xsd:string)
AnnotationAssertion(<http://purl.org/dc/terms/title> <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyTEMP.yaml> "xpoAnatomyTEMP"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyTEMP.yaml> "abnormal(ly) 'quality' of 'entity' (T)"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoAnatomyTEMP.yaml> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(owl:Thing ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> owl:Thing) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))

# Class: <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoBiologicalProcessInLocationTEMP.yaml> (abnormal(ly) 'quality' of 'entity' in 'entity' (T))

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoBiologicalProcessInLocationTEMP.yaml> "Abnormal(ly) 'quality' of 'entity' in 'entity' (Temporary definition)."^^xsd:string)
AnnotationAssertion(<http://purl.org/dc/terms/title> <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoBiologicalProcessInLocationTEMP.yaml> "xpoBiologicalProcessInLocationTEMP"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoBiologicalProcessInLocationTEMP.yaml> "abnormal(ly) 'quality' of 'entity' in 'entity' (T)"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/xpo/src/patterns/dosdp-patterns/xpoBiologicalProcessInLocationTEMP.yaml> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(owl:Thing ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> ObjectIntersectionOf(owl:Thing ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000066> owl:Thing))) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))


```


### The /patterns/definitions.owl gives us:

```

# Class: <http://purl.obolibrary.org/obo/XPO_0102262> (abnormal neurocoel morphology)

AnnotationAssertion(<http://purl.obolibrary.org/obo/IAO_0000115> <http://purl.obolibrary.org/obo/XPO_0102262> "Any unspecified morphological anomaly of the neurocoel, such as, for example, abnormal shape or colour."^^xsd:string)
AnnotationAssertion(<http://www.geneontology.org/formats/oboInOwl#hasExactSynonym> <http://purl.obolibrary.org/obo/XPO_0102262> "abnormal morphology of neurocoel"^^xsd:string)
AnnotationAssertion(rdfs:label <http://purl.obolibrary.org/obo/XPO_0102262> "abnormal neurocoel morphology"^^xsd:string)
EquivalentClasses(<http://purl.obolibrary.org/obo/XPO_0102262> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/BFO_0000051> ObjectIntersectionOf(<http://purl.obolibrary.org/obo/PATO_0000051> ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0000052> <http://purl.obolibrary.org/obo/XAO_0000252>) ObjectSomeValuesFrom(<http://purl.obolibrary.org/obo/RO_0002573> <http://purl.obolibrary.org/obo/PATO_0000460>))))


```





### Installing

A step by step series of examples that tell you how to get a development env running

Typically on linux o/s we install docker and follow the ODK installation steps.

Handy script for deployment steps [xpo_docker_deploy.sh](https://gist.github.com/pellst/17fece5f3dc8531d9d3cb5d4268fea18)


```
finished
```

End with an example of getting some data out of the system or using it for a little demo




## Running the tests

Explain how to run the automated tests for this system

# the XPO test pipeline can be run with the shell script located in /src/ontology
```
./test.sh
```

The test are run by the following statements
```

# command to run tests
script: cd src/ontology && sh run.sh make test
```



### Break down into end to end tests

Explain the purpose of these tests and why they are performed.

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```





## Deployment

Add additional notes about how to deploy this on a live system

The two aspects to the deployment. Obtaining the XPO and running the pipeline in order to build the XPO.owl and XPO.obo. 
This is build phase. Then there are the steps to release the XPO.owl and use the XPO.obo in the Anatomy Ontology Loader.

Per the Installation section. Typically on linux o/s we install docker and follow the ODK installation steps.
Handy script for deployment steps [xpo_docker_deploy.sh](https://gist.github.com/pellst/17fece5f3dc8531d9d3cb5d4268fea18)


```
cd /home/ec2-user
mkdir exports
cd /home/ec2-user/exports
curl -LOk https://github.com/obophenotype/xenopus-phenotype-ontology/archive/master.zip
unzip master.zip

cd xenopus-phenotype-ontology-master
cd /home/ec2-user/exports/xenopus-phenotype-ontology-master/src/ontology
chmod 777 run.sh 
```


# the XPO build pipeline can be run with the shell script located in /src/ontology
```
./build.sh
```

This includes the steps that can be optionally run to test and prepare-release, for which we have helper scripts

```
./test.sh
./prepare-release.sh

```



## Enhancements

We would like to add a make target to handle the addition of intersection_of to the .obo

```
Purpose is to add a target to the xpo.Makefile in order to build a .obo that includes the intersection_of in the format of:


Syntactically we can represent what we are looking for as:
[Term]
id: XPO:0103336
name: decreased size of the eye
def: "An abnormal reduction in the size of the eye." []
intersection_of: PATO_0000587^RO_0000052(XAO_0000179)^RO_0002573(PATO_0000460) ! decreased size ; inheres_in; eye; has_modifier; abnormal;
synonym: "abnormally small eye" EXACT []
is_a: XPO:0101817 ! abnormal morphology of eye


https://github.com/obophenotype/xenopus-phenotype-ontology/blob/master/src/metadata/xenbase_phenotype_annotation.csv
xenbase_phenotype_annotation.csv

Entity ID,Quality ID,Quality Name
XAO:0000179,PATO:0000587,decreased size

Determine how the mapping from  XPO:0103336 is made to the xenbase_phenotype_annotation.csv record for: XAO:0000179,PATO:0000587,decreased size


The python script to prepare the XPO needs to be integrated into the XPO build pipeline. We would benefit from a more detailed understanding of ROBOT and how it works with the transformation from OWL to OBO and specifically the java code that handles the intersection_of annotations.For now we are making do with the id_map.tsv as the data source.
xao_for_xpo.py

```

### The Makefile contains this for the XPO-simple.owl. We see that equivalent-classes-allowed none, for ELK:

```

$(ONT)-simple.owl: $(SRC) $(OTHER_SRC) $(SIMPLESEED)
	$(ROBOT) merge --input $< $(patsubst %, -i %, $(OTHER_SRC)) \
		reason --reasoner ELK --equivalent-classes-allowed none --exclude-tautologies structural \
		relax \
		remove --axioms equivalent \
		relax \
		filter --term-file $(SIMPLESEED) --select "annotations ontology anonymous self" --trim true --signature true \
		reduce -r ELK \
		query --update ../sparql/inject-subset-declaration.ru \
		annotate --ontology-iri $(ONTBASE)/$@ --version-iri $(ONTBASE)/releases/$(TODAY)/$@ --output $@.tmp.owl && mv $@.tmp.owl $@

```

### In the section # Import Modules paragraph we find

```

# seed.txt contains all referenced entities


seed.txt: $(SRC) prepare_patterns $(PATTERNDIR)/all_pattern_terms.txt
	@if [ $(IMP) = true ]; then $(ROBOT) query --use-graphs true -f csv -i $< --query ../sparql/terms.sparql $@.tmp &&\
	cat $@.tmp $(PATTERNDIR)/all_pattern_terms.txt | sort | uniq >  $@; fi


# Generate terms.txt for each import.  (Assume OBO-style Possibly hacky step?)
# Should be able to drop this if robot can just take a big messy list of terms as input.

imports/%_terms_combined.txt: seed.txt imports/%_terms.txt
	@if [ $(IMP) = true ]; then cat $^ | grep -v ^# | sort | uniq >  $@; fi


```



### See the section # Patterns (experimental)

```

# Generating the individual pattern modules and merging them into definitions.owl
$(PATTERNDIR)/definitions.owl: prepare_patterns update_patterns $(individual_patterns_default)   $(individual_patterns_manual) $(individual_patterns_anatomy)
	@if [ $(PAT) = true ]; then $(ROBOT) merge $(addprefix -i , $(individual_patterns_default))   $(addprefix -i , $(individual_patterns_manual)) $(addprefix -i , $(individual_patterns_anatomy)) annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl  --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions.owl -o definitions.ofn && mv definitions.ofn $@; fi

$(PATTERNDIR)/data/default/%.ofn: $(PATTERNDIR)/data/default/%.tsv $(PATTERNDIR)/dosdp-patterns/%.yaml $(SRC) all_imports .FORCE
	@if [ $(PAT) = true ]; then $(DOSDPT) generate --catalog=catalog-v001.xml --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true --outfile=$@; fi



$(PATTERNDIR)/data/manual/%.ofn: $(PATTERNDIR)/data/manual/%.tsv $(PATTERNDIR)/dosdp-patterns/%.yaml $(SRC) all_imports .FORCE
	@if [ $(PAT) = true ]; then $(DOSDPT) generate --catalog=catalog-v001.xml --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true --outfile=$@; fi

$(PATTERNDIR)/data/anatomy/%.ofn: $(PATTERNDIR)/data/anatomy/%.tsv $(PATTERNDIR)/dosdp-patterns/%.yaml $(SRC) all_imports .FORCE
	@if [ $(PAT) = true ]; then $(DOSDPT) generate --catalog=catalog-v001.xml --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true --outfile=$@; fi



# Generating the seed file from all the TSVs. If Pattern generation is deactivated, we still extract a seed from definitions.owl
$(PATTERNDIR)/all_pattern_terms.txt: $(pattern_term_lists_default)   $(pattern_term_lists_manual) $(pattern_term_lists_anatomy) $(PATTERNDIR)/pattern_owl_seed.txt
	@if [ $(PAT) = true ]; then cat $^ | sort | uniq > $@; else $(ROBOT) query --use-graphs true -f csv -i ../patterns/definitions.owl --query ../sparql/terms.sparql $@; fi

$(PATTERNDIR)/pattern_owl_seed.txt: $(PATTERNDIR)/pattern.owl
	@if [ $(PAT) = true ]; then $(ROBOT) query --use-graphs true -f csv -i $< --query ../sparql/terms.sparql $@; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	@if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

.PHONY: prepare_patterns
prepare_patterns:
	touch $(pattern_term_lists_default)   $(pattern_term_lists_manual) $(pattern_term_lists_anatomy) &&\
  touch $(individual_patterns_default)   $(individual_patterns_manual) $(individual_patterns_anatomy)


$(PATTERNDIR)/data/manual/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/manual/%.tsv .FORCE
	@if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

$(PATTERNDIR)/data/anatomy/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/anatomy/%.tsv .FORCE
	@if [ $(PAT) = true ]; then $(DOSDPT) terms --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi



```



### ROBOT is an OBO Tool

[![Build Status](https://travis-ci.org/ontodev/robot.svg?branch=master)](https://travis-ci.org/ontodev/robot)
[![Javadocs](https://www.javadoc.io/badge/org.obolibrary.robot/robot-core.svg)](https://www.javadoc.io/doc/org.obolibrary.robot/robot-core)


The integration tests are executed with `mvn verify`, which is run on all pull requests via Travis CI.

Embedded examples for testing must use Markdown [indented code blocks](https://github.github.com/gfm/#indented-code-blocks), where each line begins with four spaces. To provide code examples that *will not* be tested, use [fenced code blocks](https://github.github.com/gfm/#fenced-code-blocks) instead, beginning and ending with three backticks (\`\`\`).

```
robot-core/src/main/resources/Makefile-ROBOT
   Currently the main purpose is to define some standard build targets, variables, and to provide a standard way
   of obtaining the robot executable, e.g. for running in travis
```


```
util/release.sh
#!/usr/bin/env nix-shell
#! nix-shell -i bash -p git travis jq semver-tool

```

#### This script helps to automate ROBOT releases.

```
step "Check Travis"
travis status --skip-version-check --exit-code --fail-pending

step "Check Jenkins"
curl --silent "https://build.obolibrary.io/job/ontodev/job/robot/job/master/lastBuild/api/json" | jq --exit-status '.result | test("SUCCESS")'
```




## Built With

* [ODK](https://github.com/INCATools/ontology-development-kit) - The framework
* [Robot](https://github.com/ontodev/robot) - The OBO Tool
* [Travis](https://travis-ci.org/ontodev/robot) - CI
* [zenodo](https://github.com/zenodo/zenodo) - digital library or document repository on the web



## Contributing

Please read [CONTRIBUTING.md](https://github.com/obophenotype/xenopus-phenotype-ontology/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [github](https://github.com/obophenotype/xenopus-phenotype-ontology) for versioning.





## Authors

* **Xenbase Development Team** - *Initial work* - [Xenbase](https://xenbase.org)

See also the list of [contributors](https://github.com/obophenotype/xenopus-phenotype-ontology/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [Xenbase Development Team](http://www.xenbase.org)
* Inspiration
* etc

