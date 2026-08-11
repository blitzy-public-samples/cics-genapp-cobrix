******************************************************************
*  COPYBOOK  : GOKSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : KS
******************************************************************
 01  RT-OKS-RATING.

          03 RT-OKS-TERRITORY-CODE            PIC X(3).
          03 RT-OKS-CLASS-CODE                PIC X(4).
          03 RT-OKS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OKS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OKS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OKS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OKS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OKS-RATED-PREMIUM             PIC 9(9)V9(2).
